# General python import statements ------------------------------------
import datetime

# Django-specific import statements -----------------------------------
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Max

# Matplotlib specific import statements -------------------------------
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Bwhist
from custom.aggregate import CountCase


def readhist(request, fingerprint):
    """
    Create a graph of read bandwidth history for the last twenty-four
    hours available for a router with a given fingerprint.

    Currently, this method simply displays the most recent information
    available; it is not necessary that the router be active recently.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router to gather
        bandwidth history information on.
    @rtype: HttpRequest
    @return: A PNG image that is the graph of the read bandwidth
        history information for the given router.
    """
    from django.core.exceptions import ObjectDoesNotExist
    import matplotlib
    from matplotlib.backends.backend_agg import \
            FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.2
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.87

    last_hist = Bwhist.objects.filter(fingerprint=fingerprint)\
                .order_by('-date')[:1][0]

    t_start, t_end, tr_list = last_hist.read

    recent_date = last_hist.date
    recent_time = datetime.datetime.combine(recent_date,
                  datetime.time())

    # It's possible that we might be missing some entries at the
    # beginning; add values of 0 in this case.
    tr_list[0:0] = ([0] * t_start)

    # We want to have 96 data points in our graph; if we don't have
    # them, get some data points from the day before, if we can.
    to_fill = 96 - len(tr_list)

    start_time = recent_time - datetime.timedelta(\
                 minutes=(15 * to_fill))
    end_time = start_time + datetime.timedelta(days=1) - \
               datetime.timedelta(minutes=15)

    # If less than 96 entries in the array, get earlier entries.
    # If they don't exist, fill in the array with '0' values.
    if to_fill:
        day_before = last_hist.date - datetime.timedelta(days=1)

        try:
            day_before_hist = Bwhist.objects.get(\
                    fingerprint=fingerprint,
                    date=str(day_before))
            y_start, y_end, y_list = day_before_hist.read
            y_list.extend([0] * (95 - y_end))
            y_list[0:0] = ([0] * y_start)

        except ObjectDoesNotExist:
            y_list = ([0] * 96)
        tr_list[0:0] = y_list[(-1 * to_fill):]

    fig = Figure(facecolor='white', edgecolor='black', figsize=(6, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    # Return bytes per second, not total bandwidth for 15 minutes.
    bps = map(lambda x: x / (15 * 60), tr_list)
    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = "%0*d:%0*d" % (2, to_add_date.hour,
                                    2, to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    # Draw the graph and give the graph a light shade underneath it.
    ax.plot(dates, bps, color='#68228B')
    ax.fill_between(dates, 0, bps, color='#DAC8E2')

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize='8', fontweight='bold')

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Average Bandwidth Read History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def writehist(request, fingerprint):
    """
    Create a graph of written bandwidth history for the last twenty-four
    hours available for a router with a given fingerprint.

    Currently, this method simply displays the most recent information
    available; it is not necessary that the router be active recently.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router to gather
        bandwidth history information on.
    @rtype: HttpRequest
    @return: A PNG image that is the graph of the written bandwidth
        history information for the given router.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.2
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.87

    last_hist = Bwhist.objects.filter(fingerprint=fingerprint)\
                .order_by('-date')[:1][0]

    t_start, t_end, tr_list = last_hist.written

    recent_date = last_hist.date
    recent_time = datetime.datetime.combine(recent_date,
                  datetime.time())

    # It's possible that we might be missing some entries at the
    # beginning; add values of 0 in this case.
    tr_list[0:0] = ([0] * t_start)

    # We want to have 96 data points in our graph; if we don't have
    # them, get some data points from the day before, if we can.
    to_fill = 96 - len(tr_list)

    start_time = recent_time - datetime.timedelta(\
                 minutes=(15 * to_fill))
    end_time = start_time + datetime.timedelta(days=1) - \
               datetime.timedelta(minutes=15)

    # If less than 96 entries in the array, get earlier entries.
    # If they don't exist, fill in the array with '0' values.
    if to_fill:
        day_before = last_hist.date - datetime.timedelta(days=1)
        try:
            day_before_hist = Bwhist.objects.get(\
                    fingerprint=fingerprint,
                    date=str(day_before))
            y_start, y_end, y_list = day_before_hist.written
            y_list.extend([0] * (95 - y_end))
            y_list[0:0] = ([0] * y_start)
        except ObjectDoesNotExist:
            y_list = ([0] * 96)
        tr_list[0:0] = y_list[(-1 * to_fill):]

    fig = Figure(facecolor='white', edgecolor='black', figsize=(6, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    # Return bytes per second, not total bandwidth for 15 minutes.
    bps = map(lambda x: x / (15 * 60), tr_list)

    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = "%0*d:%0*d" % (2, to_add_date.hour,
                                    2, to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    # Draw the graph and give it a nice shade underneath it.
    ax.plot(dates, bps, color='#66CD00')
    ax.fill_between(dates, 0, bps, color='#D9F3C0')

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize='8', fontweight='bold')

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Average Bandwidth Write History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response
    
def bycountrycode(request):
    """
    Return a graph representing the number of routers by country code.

    @rtype: HttpResponse
    @return: A graph representing the number of routers by country
        code as an HttpResponse object.
    """
    import matplotlib
    from matplotlib.backends.backend_agg import \
            FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.06

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)\
                    .extra(select={'geoip': 'geoip_lookup(address)'})

    country_map = {}

    for entry in statusentries:
        # 'geoip' is a string, where the second and third characters
        # make the country code.
        country = entry.geoip[1:3]
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    x_index = matplotlib.numpy.arange(num_params)

    fig = Figure(facecolor='white', edgecolor='black', figsize=(12, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.5
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')

    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(keys, fontsize='8', fontweight='bold',
                       rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Number of Routers by Country Code",
                 fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def exitbycountrycode(request):
    """
    Return a graph representing the number of exit routers
    by country code.

    @rtype: HttpResponse
    @return: A graph representing the number of exit routers by country
        code as an HttpResponse object.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.06

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va,
                    isexit=1)\
                    .extra(select={'geoip': 'geoip_lookup(address)'})

    country_map = {}

    for entry in statusentries:
        # 'geoip' is a string, where the second and third characters
        # make the country code.
        country = entry.geoip[1:3]
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    x_index = matplotlib.numpy.arange(num_params)

    fig = Figure(facecolor='white', edgecolor='black', figsize=(12, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.6
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')

    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(keys, fontsize='8', fontweight='bold',
                       rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Number of Exit Routers by Country Code",
                 fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def bytimerunning(request):
    """
    Return a graph representing the uptime of routers in the Tor
    network.

    @rtype: HttpResponse
    @return: A graph representing the uptime of routers in the
        Tor network as an HttpResponse object.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.04

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)

    uptime_map = {}

    for entry in statusentries:
        # The uptime in weeks is seconds / (seconds/min * min/hour
        # * hour/day * day/week), where / signifies floor division.
        weeks = entry.descriptorid.uptime / (60 * 60 * 24 * 7)
        if weeks in uptime_map:
            uptime_map[weeks] += 1
        else:
            uptime_map[weeks] = 1

    keys = sorted(uptime_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [uptime_map[key] for key in keys]

    x_index = matplotlib.numpy.arange(num_params)

    fig = Figure(facecolor='white', edgecolor='black', figsize=(12, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.5
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')

    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(keys, fontsize='9', fontweight='bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Number of Routers by Time Running (Weeks)",
                 fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def byobservedbandwidth(request):
    """
    Return a graph representing the observed bandwidth of the
    routers in the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the observed bandwidth of the
        routers in the Tor network.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.08
    matplotlib.rcParams['figure.subplot.right'] = 0.98
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.19

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)

    bw_map = {}
    keys = ['0-10', '11-20', '21-50', '51-100', '101-500', '501-1000',
            '1001-2000', '2001-3000', '3001-5000', '5001+']
    for key in keys:
        bw_map[key] = 0

    for entry in statusentries:
        kbps = entry.descriptorid.bandwidthobserved / 1024
        if (0 <= kbps <= 10):
            bw_map['0-10'] += 1
        elif (101 <= kbps <= 500):
            bw_map['101-500'] += 1
        elif (11 <= kbps <= 20):
            bw_map['11-20'] += 1
        elif (21 <= kbps <= 50):
            bw_map['21-50'] += 1
        elif (51 <= kbps <= 100):
            bw_map['51-100'] += 1
        elif (501 <= kbps <= 1000):
            bw_map['501-1000'] += 1
        elif (1001 <= kbps <= 2000):
            bw_map['1001-2000'] += 1
        elif (2001 <= kbps <= 3000):
            bw_map['2001-3000'] += 1
        elif (3001 <= kbps <= 5000):
            bw_map['3001-5000'] += 1
        elif (5001 <= kbps):
            bw_map['5001+'] += 1

    num_params = len(keys)
    xs = range(num_params)
    ys = [bw_map[key] for key in keys]

    x_index = matplotlib.numpy.arange(num_params)

    fig = Figure(facecolor='white', edgecolor='black', figsize=(6, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.5
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')

    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(keys, fontsize='8', fontweight='bold',
                       rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Number of Routers by Observed Bandwidth (KB/sec)",
                 fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def byplatform(request):
    """
    Return a graph representing the platforms of the active relays
    in the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the platforms of the active relays
        in the Tor network as an HttpResponse object.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.08
    matplotlib.rcParams['figure.subplot.right'] = 0.98
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.05

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)

    platform_map = {}
    keys = ['Linux', 'Windows', 'FreeBSD', 'Darwin', 'OpenBSD',
            'NetBSD', 'SunOS']
    for platform in keys:
        platform_map[platform] = 0

    platform_map['Unknown'] = 0

    for entry in statusentries:
        platform = entry.descriptorid.platform
        for key in keys:
            if key in platform:
                platform_map[key] += 1
                break
        # 'else' statement only runs if the for loop terminates
        # normally -- that is, without a break.
        else:
            platform_map['Unknown'] += 1

    keys.append('Unknown')

    num_params = len(keys)
    xs = range(num_params)
    ys = [platform_map[key] for key in keys]

    x_index = matplotlib.numpy.arange(num_params)

    fig = Figure(facecolor='white', edgecolor='black', figsize=(6, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.5
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')

    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(keys, fontsize='9', fontweight='bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Number of Routers by Platform",
                 fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response
    
def aggregatesummary(request):
    """
    Return a graph representing an aggregate summary of the routers on
    the network as an HttpResponse object.

    @rtype: HttpResponse
    @return: A graph representing an aggregate summary of the routers on
        the Tor network.
    """

    # Draw the graph such that the labels and title are visible,
    # and remove excess whitespace.
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.99
    matplotlib.rcParams['figure.subplot.top'] = 0.92
    matplotlib.rcParams['figure.subplot.bottom'] = 0.04

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(validafter=last_va)

    total = statusentries.count()
    counts = Statusentry.objects.filter(validafter=last_va).aggregate(\
            isauthority=CountCase('isauthority', when=True),
            isbaddirectory=CountCase('isbaddirectory', when=True),
            isbadexit=CountCase('isbadexit', when=True),
            isexit=CountCase('isexit', when=True),
            isfast=CountCase('isfast', when=True),
            isguard=CountCase('isguard', when=True),
            isnamed=CountCase('isnamed', when=True),
            isstable=CountCase('isstable', when=True),
            isrunning=CountCase('isrunning', when=True),
            isvalid=CountCase('isvalid', when=True),
            isv2dir=CountCase('isv2dir', when=True))

    keys = ['isauthority', 'isbaddirectory', 'isbadexit', 'isexit',
            'isfast', 'isguard', 'isnamed', 'isstable', 'isrunning',
            'isvalid', 'isv2dir']
    labels = ['Total', 'Authority', 'BadDirectory', 'BadExit', 'Exit',
            'Fast', 'Guard', 'Named', 'Stable', 'Running', 'Valid',
            'V2Dir']
    num_params = len(labels)
    xs = range(num_params)
    x_index = matplotlib.numpy.arange(num_params)

    ys = []
    ys.append(total)
    for count in keys:
        ys.append(counts[count])

    fig = Figure(facecolor='white', edgecolor='black', figsize=(12, 4),
                 frameon=False)
    ax = fig.add_subplot(111)

    bar_width = 0.5
    ax.bar(xs, ys, color='#66CD00', width=bar_width)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (bar_width / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize='8', horizontalalignment='center')
    ax.set_xticks(x_index + (bar_width / 2.0))
    ax.set_xticklabels(labels, fontsize='9', fontweight='bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')
        tick.label1.set_fontweight('bold')

    ax.set_title("Aggregate Summary -- Number of Routers Matching "
            + "Specified Criteria", fontsize='12', fontweight='bold')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

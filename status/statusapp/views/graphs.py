"""
Views for statusapp that involve creating dynamic graphs.
"""
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


# TODO: Get rid of "magic numbers in graphs", so that the graphs are
# more easily customizable by future maintainers.
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
    # Width and height of the graph in pixels
    WIDTH = 480
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 42
    BOTTOM_MARGIN = 32
    LEFT_MARGIN = 98
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
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
    ax.set_xticklabels(times, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Average Bandwidth Read History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 480
    HEIGHT = 320
    # Space in pixels given around plot
    # NOTE: be careful with these margins; some values can cause
    # irregular behavior
    TOP_MARGIN = 42
    BOTTOM_MARGIN = 32
    LEFT_MARGIN = 98
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
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
    ax.set_xticklabels(times, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Average Bandwidth Write History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 960
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 19
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(keys, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT, rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Number of Routers by Country Code",
                 fontsize='12', fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 960
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 19
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(keys, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT, rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Number of Exit Routers by Country Code",
                 fontsize='12', fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 960
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 19
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '9'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(keys, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Number of Routers by Time Running (Weeks)",
                 fontsize='12', fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 480
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 64
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Define the ranges for the graph, a list of 2-tuples of ints.
    RANGES = [(0, 10), (11, 20), (21, 50), (51, 100), (101, 500),
              (501, 1000), (1001, 2000), (2001, 3000), (3001, 5000)]

    # This next part is here to give me ideas.
    #import math
    #RANGES = []
    #i = 0
    #granularity = 10
    #while (i < 10000):
    #    lower = i
    #    upper = lower + lower / granularity + 10
    #    round_to = -1*(int(math.log(upper, 10)) - 1)
    #    upper = int(round(upper, round_to))
    #    RANGES.append((lower, upper))
    #    i = upper + 1

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

    last_va = Statusentry.objects.aggregate(\
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)

    bw_map = {}
    excess = RANGES[-1][1] + 1

    for rng in RANGES:
        bw_map[rng] = 0
    bw_map[excess] = 0

    for entry in statusentries:
        kbps = entry.descriptorid.bandwidthobserved / 1024

        # Linear search
        # for lower, upper in ranges:
        #     if lower <= kbps <= upper:
        #         bw_map[lower, upper] += 1
        #         break
        # else:
        #     bw_map[excess] += 1

        # Binary search
        # Is there a way to clean up this bit? It could be its own
        # function...
        rngs = RANGES
        while (rngs and (not rngs[len(rngs) / 2][0] <= kbps <= \
                             rngs[len(rngs) / 2][1])):
            if rngs[len(rngs) / 2][0] > kbps:
                rngs = rngs[:(len(rngs) / 2)]
            else:
                rngs = rngs[(len(rngs) / 2 + 1):]
        if rngs:
            bw_map[rngs[len(rngs) / 2][0], rngs[len(rngs) / 2][1]] += 1
        else:
            bw_map[excess] += 1


    num_params = len(bw_map)
    xs = range(num_params)
    ys = [bw_map[lower, upper] for lower, upper in RANGES]
    ys.append(bw_map[excess])

    labels = ['%s-%s' % (lower, upper) for lower, upper in RANGES]
    labels.append('%s+' % excess)

    x_index = matplotlib.numpy.arange(num_params)

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(labels, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT, rotation='vertical')

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Number of Routers by Observed Bandwidth (KB/sec)",
                 fontsize='12', fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 480
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 19
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '9'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(keys, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Number of Routers by Platform",
                 fontsize='12', fontweight=FONT_WEIGHT)

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
    # Width and height of the graph in pixels
    WIDTH = 960
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 25
    BOTTOM_MARGIN = 19
    LEFT_MARGIN = 38
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '9'
    Y_FONT_SIZE = '9'
    LABEL_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'
    BAR_WIDTH = 0.5

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

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

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    ax.bar(xs, ys, color='#66CD00', width=BAR_WIDTH)

    # Label the height of each bar.
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (ax.get_ylim()[1] / 100), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(labels, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Aggregate Summary -- Number of Routers Matching "
               + "Specified Criteria", fontsize='12',
                 fontweight=FONT_WEIGHT)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

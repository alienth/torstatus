"""
Views for statusapp that involve creating dynamic graphs.
"""
# Python-specific import statements -----------------------------------
from copy import copy
import datetime

# Django-specific import statements -----------------------------------
from django.db.models import Max
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

# Matplotlib-specific import statements -------------------------------
import matplotlib
from pylab import legend
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

# TorStatus specific import statements --------------------------------
from statusapp.models import Bwhist, TotalBandwidth, NetworkSize, \
        ActiveRelay
from custom.aggregate import CountCase

# Default parameters to be used with the graphs. Each graph may change
# certain parameters, but a default dictionary enforces uniformity
# on the graphs.
DEFAULT_PARAMS = {'WIDTH': 960, 'HEIGHT': 320, 'TOP_MARGIN': 25,
                  'BOTTOM_MARGIN': 19, 'LEFT_MARGIN': 38,
                  'RIGHT_MARGIN': 5, 'X_FONT_SIZE': '8',
                  'Y_FONT_SIZE': '9', 'LABEL_FONT_SIZE': '8',
                  'LABEL_FLOAT': 3, 'LABEL_ROT': 'horizontal',
                  'FONT_WEIGHT': 'bold', 'BAR_WIDTH': 0.5,
                  'COLOR': '#005500', 'TITLE': ''}


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
    return draw_line_graph(fingerprint, 'Read', '#68228B', '#DAC8E2')


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
    return draw_line_graph(fingerprint, 'Written', '#66CD00', '#D9F3C0')


@cache_page(60 * 15)
def bycountrycode(request):
    """
    Return a graph representing the number of routers by country code.

    @rtype: HttpResponse
    @return: A graph representing the number of routers by country
        code as an HttpResponse object.
    """
    params = copy(DEFAULT_PARAMS)
    params['LABEL_ROT'] = 'vertical'
    params['TITLE'] = 'Number of Routers by Country Code'

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va)

    # Build a dictionary mapping countries to the number of relays
    # from that country
    country_map = {}
    for relay in relays:
        country = relay.country
        if country is None:
            country = '??'
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 15)
def exitbycountrycode(request):
    """
    Return a graph representing the number of exit routers
    by country code.

    @rtype: HttpResponse
    @return: A graph representing the number of exit routers by country
        code as an HttpResponse object.
    """
    params = copy(DEFAULT_PARAMS)
    # Make labels vertical to increase readability and minimize
    # graph width
    params['LABEL_ROT'] = 'vertical'
    params['TITLE'] = 'Number of Exit Routers by Country Code'

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va, isexit=1)

    # Build a dictionary mapping countries to the number of relays
    # from that country
    country_map = {}
    for relay in relays:
        country = relay.country
        if country is None:
            country = '??'
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 15)
def bytimerunning(request):
    """
    Return a graph representing the uptime of routers in the Tor
    network.

    @rtype: HttpResponse
    @return: A graph representing the uptime of routers in the
        Tor network as an HttpResponse object.
    """
    params = copy(DEFAULT_PARAMS)
    params['X_FONT_SIZE'] = '9'
    params['TITLE'] = 'Number of Routers by Time Running (weeks)'

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va)

    uptime_map = {}

    # TODO: This step is very inefficient; a custom SUM(CASE WHERE...
    # should probably be written.
    for relay in relays:
        # The uptime in weeks is seconds / (seconds/min * min/hour
        # * hour/day * day/week), where / signifies floor division.
        uptimedays = relay.uptimedays
        if uptimedays is None:
            continue
        weeks = relay.uptimedays / 7
        if weeks in uptime_map:
            uptime_map[weeks] += 1
        else:
            uptime_map[weeks] = 1

    keys = sorted(uptime_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [uptime_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 15)
def byobservedbandwidth(request):
    """
    Return a graph representing the observed bandwidth of the
    routers in the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the observed bandwidth of the
        routers in the Tor network.
    """
    params = copy(DEFAULT_PARAMS)
    # Width and height of the graph in pixels
    params['WIDTH'] = 480
    params['HEIGHT'] = 320
    # Space in pixels given around plot
    params['TOP_MARGIN'] = 25
    params['BOTTOM_MARGIN'] = 64
    params['LEFT_MARGIN'] = 38
    params['RIGHT_MARGIN'] = 5
    params['LABEL_ROT'] = 'vertical'
    params['TITLE'] = 'Number of Routers by Observed Bandwidth (KB/sec)'

    # Define the ranges for the graph, a list of 2-tuples of ints
    RANGES = [(0, 10), (11, 20), (21, 50), (51, 100), (101, 500),
              (501, 1000), (1001, 2000), (2001, 3000), (3001, 5000),
              (5001, 10000)]

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va)

    # Get the highest defined limit in RANGES
    excess = RANGES[-1][1] + 1

    # Initialize a dictionary mapping bandwidth ranges to number of
    # routers
    bw_map = {}
    for rng in RANGES:
        bw_map[rng] = 0
    bw_map[excess] = 0

    for relay in relays:
        kbps = relay.bandwidthkbps

        # Binary search -- extensible to finer-grained ranges
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

    return draw_bar_graph(xs, ys, labels, params)


@cache_page(60 * 15)
def byplatform(request):
    """
    Return a graph representing the platforms of the active relays
    in the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the platforms of the active relays
        in the Tor network as an HttpResponse object.
    """
    params = copy(DEFAULT_PARAMS)
    params['WIDTH'] = 480
    params['HEIGHT'] = 320
    params['X_FONT_SIZE'] = '9'
    params['TITLE'] = 'Number of Routers by Platform'

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va)

    platform_map = {}
    keys = ['Linux', 'Windows', 'FreeBSD', 'Darwin', 'OpenBSD',
            'NetBSD', 'SunOS']
    for platform in keys:
        platform_map[platform] = 0

    platform_map['Unknown'] = 0

    # TODO: Inefficient for the same reason that the observed bandwidth
    # graph is inefficient; a custom SUM(CASE WHERE...) should be
    # necessary here
    for relay in relays:
        platform = relay.platform
        if platform is None:
            platform_map['Unknown'] += 1
            continue
        for key in keys:
            if key in platform:
                platform_map[key] += 1
                break
        # 'else' statement only runs if the for loop terminates
        # normally -- that is, without a break
        else:
            platform_map['Unknown'] += 1

    keys.append('Unknown')

    num_params = len(keys)
    xs = range(num_params)
    ys = [platform_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 15)
def aggregatesummary(request):
    """
    Return a graph representing an aggregate summary of the routers on
    the network as an HttpResponse object.

    @rtype: HttpResponse
    @return: A graph representing an aggregate summary of the routers on
        the Tor network.
    """
    params = copy(DEFAULT_PARAMS)
    params['X_FONT_SIZE'] = '9'
    params['TITLE'] = 'Aggregate Summary -- Number of Routers Matching' \
                    + ' Specified Criteria'

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    relays = ActiveRelay.objects.filter(validafter=last_va)

    total = relays.count()
    counts = ActiveRelay.objects.filter(validafter=last_va).aggregate(
             isauthority=CountCase('isauthority', when=True),
             isbaddirectory=CountCase('isbaddirectory', when=True),
             isbadexit=CountCase('isbadexit', when=True),
             isexit=CountCase('isexit', when=True),
             isfast=CountCase('isfast', when=True),
             isguard=CountCase('isguard', when=True),
             ishibernating=CountCase('ishibernating', when=True),
             isnamed=CountCase('isnamed', when=True),
             isstable=CountCase('isstable', when=True),
             isrunning=CountCase('isrunning', when=True),
             isvalid=CountCase('isvalid', when=True),
             isv2dir=CountCase('isv2dir', when=True))

    keys = ['isauthority', 'isbaddirectory', 'isbadexit', 'isv2dir',
            'isexit', 'isfast', 'isguard', 'ishibernating', 'isnamed',
            'isstable', 'isrunning', 'isvalid']
    labels = ['Total', 'Authority', 'Bad Directory', 'Bad Exit',
              'Directory', 'Exit', 'Fast', 'Guard', 'Hibernating',
              'Named', 'Stable', 'Running', 'Valid']
    num_params = len(labels)
    xs = range(num_params)

    ys = []
    ys.append(total)
    for count in keys:
        ys.append(counts[count])

    return draw_bar_graph(xs, ys, labels, params)


@cache_page(60 * 15)
def networktotalbw(request):
    """
    Return a graph representing the total bandwidth of the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the total bandwidth of the
        Tor Network.
    """
    # Graph presentation parameters -----------------------------------
    HEIGHT = 160
    WIDTH = 440
    TOP_MARGIN = 8
    BOTTOM_MARGIN = 28
    LEFT_MARGIN = 50
    RIGHT_MARGIN = 50
    X_FONT_SIZE = 8
    Y_FONT_SIZE = 8
    LABEL_FONT_SIZE = 8
    LABEL_ROT = 'horizontal'
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

    # TotalBandwidth Plot --------------------------------------------
    # Get last 93 TotalBandwidth entries
    tbw_entries = list(TotalBandwidth.objects.all().order_by(
                       '-date')[:93])

    # Should be 93, but could be less if not enough TotalBandwidth
    # entries are present
    data_points = len(tbw_entries)
    xs = range(data_points)

    ys_bwobserved = []
    for i in range(data_points - 1, -1, -1):
        ys_bwobserved.append(
                      tbw_entries[i].bwobserved / float(1024**2))

    times = []
    start_date = tbw_entries[-1].date
    for i in range(0, data_points, 7):
        to_add_date = start_date + datetime.timedelta(days=(1 * i))
        to_add_str = "%s-%0*d" % (to_add_date.month,
                                  2, to_add_date.day)
        times.append(to_add_str)

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80

    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)

    # Draw bandwidth observed line
    ax1 = fig.add_subplot(111)

    observed_bw = ax1.plot(xs, ys_bwobserved, color='#68228B',
                           label='Observed Bandwidth')

    # Shade the area below the graph lightly
    ax1.fill_between(xs, 0, ys_bwobserved, color='#DAC8E2')

    # Label the graph with appropriate colors and fontsizes
    ax1.set_xlabel("Date (GMT)", fontsize='8', fontweight=FONT_WEIGHT)
    ax1.set_xticks(range(0, data_points, 7))
    ax1.set_xticklabels(times, fontsize=X_FONT_SIZE,
                        fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    ax1.set_ylabel("Bandwidth (MiB)",
                  fontsize='8', fontweight=FONT_WEIGHT)

    for tick in ax1.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    for tick in ax1.get_yticklabels():
        tick.set_color('#68228B')

    # Relays Plot -----------------------------------------------------
    net_size = list(NetworkSize.objects.all().order_by('-date')[:93])

    # Assume that the dates in net_size are the same as in tbw_entries,
    # but assert it, just to be paranoid.
    assert net_size[0].date == tbw_entries[0].date
    assert net_size[-1].date == tbw_entries[-1].date

    ys = []
    for i in range(data_points - 1, -1, -1):
        ys.append(net_size[i].avg_running)

    # Draw average relays running line using same 'xs' as before.
    ax2 = ax1.twinx()
    active_relays = ax2.plot(xs, ys, color='#005500',
                             label='Average Active Relays')

    # Label the graph with appropriate colors and fontsizes
    ax2.set_xticks(range(0, data_points, 7))
    ax2.set_xticklabels(times, fontsize=X_FONT_SIZE,
                        fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    ax2.set_ylabel('Relays', fontsize='8', fontweight=FONT_WEIGHT)

    for tick in ax2.yaxis.get_major_ticks():
        tick.label2.set_fontsize(Y_FONT_SIZE)
        tick.label2.set_fontweight(FONT_WEIGHT)

    for tick in ax2.get_yticklabels():
        tick.set_color('#005500')

    # Label entire graph
    fontparam = matplotlib.font_manager.FontProperties(
                size=8, weight='bold')

    # TODO: put both labels in one legend. How?
    ax1.legend(prop=fontparam, loc='lower left')
    ax2.legend(prop=fontparam, loc='lower right')

    # TODO: Make a grid that works for both lines
    # (Set tick marks such that a grid applies to both lines)
    ax1.set_ylim(ymin=0)
    ax1.set_xlim(xmin=0)
    ax2.set_xlim(xmin=0)
    ax1.yaxis.set_major_locator(MaxNLocator(5))
    ax2.yaxis.set_major_locator(MaxNLocator(5))
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def draw_bar_graph(xs, ys, labels, params):
    """
    Draws a bar graph, given data points, labels, and presentation
    parameters.

    @type xs: C{list}
    @param xs: The x values to be plotted.
    @type ys: C{list}
    @param ys: The y values to be plotted.
    @type labels: C{list} of C{string}
    @param labels: The labels to be used for each data point, where
        C{labels[i]} labels C{(xs[i], ys[i])}.
    @type params: C{dict} of C{string} and C{int}
    @param params: Parameters specifying how the graph is to be drawn.
        Params must contain the keys: WIDTH, HEIGHT, TOP_MARGIN,
        BOTTOM_MARGIN, LEFT_MARGIN, RIGHT_MARGIN, X_FONT_SIZE,
        Y_FONT_SIZE, LABEL_FONT_SIZE, FONT_WEIGHT, BAR_WIDTH,
        COLOR, LABEL_FLOAT, LABEL_ROT, and TITLE.
    @rtype: HttpResponse
    @return: The graph as specified by the parameters given.
    """
    ## Get the parameters from the params dictionary
    # Width and height of the graph in pixels
    WIDTH = params['WIDTH']
    HEIGHT = params['HEIGHT']
    # Space in pixels given around plot
    TOP_MARGIN = params['TOP_MARGIN']
    BOTTOM_MARGIN = params['BOTTOM_MARGIN']
    LEFT_MARGIN = params['LEFT_MARGIN']
    RIGHT_MARGIN = params['RIGHT_MARGIN']
    # Font sizes, in pixels
    X_FONT_SIZE = params['X_FONT_SIZE']
    Y_FONT_SIZE = params['Y_FONT_SIZE']
    LABEL_FONT_SIZE = params['LABEL_FONT_SIZE']
    # How many pixels above each bar the labels should be
    LABEL_FLOAT = params['LABEL_FLOAT']
    # How the labels should be presented
    LABEL_ROT = params['LABEL_ROT']
    # Font weight used for labels and titles
    FONT_WEIGHT = params['FONT_WEIGHT']
    BAR_WIDTH = params['BAR_WIDTH']
    COLOR = params['COLOR']
    # Title of graph
    TITLE = params['TITLE']

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

    # Draw the figure.
    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    # Plot the data.
    ax.bar(xs, ys, color=COLOR, width=BAR_WIDTH)

    # Label the height of each bar.
    label_float_ydist = ax.get_ylim()[1] * LABEL_FLOAT / (
                        HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)
    num_params = len(xs)
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (label_float_ydist), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    x_index = matplotlib.numpy.arange(num_params)
    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(labels, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title(TITLE, fontsize='12', fontweight=FONT_WEIGHT)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response


def draw_line_graph(fingerprint, bwtype, color, shade):
    """
    Draws a line graph with given data points and display parameters.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router that the graph
        is to be drawn for.
    @type bwtype: C{string}
    @param bwtype: Either 'read' or 'written', depending on whether the
        graph to be drawn will be of recent read bandwidth or recent
        written bandwdith.
    @type color: C{string}
    @param color: The color to draw the line graph with.
    @type shade: C{string}
    @param shade: The color to shade under the line graph.
    @rtype: HttpResponse
    @return: The graph as specified by the parameters given.
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

    if bwtype == 'Read':
        t_start, t_end, tr_list = last_hist.read
    elif bwtype == 'Written':
        t_start, t_end, tr_list = last_hist.written

    recent_date = last_hist.date
    recent_time = datetime.datetime.combine(recent_date,
                  datetime.time())

    # It's possible that we might be missing some entries at the
    # beginning; add values of 0 in this case
    tr_list[0:0] = ([0] * t_start)

    # We want to have 96 data points in our graph; if we don't have
    # them, get some data points from the day before, if we can
    to_fill = 96 - len(tr_list)

    start_time = recent_time - datetime.timedelta(
                 minutes=(15 * to_fill))
    end_time = start_time + datetime.timedelta(
               days=1) - datetime.timedelta(minutes=15)

    # If less than 96 entries in the array, get earlier entries.
    # If they don't exist, fill in the array with '0' values.
    if to_fill:
        day_before = last_hist.date - datetime.timedelta(days=1)

        try:
            day_before_hist = Bwhist.objects.get(
                    fingerprint=fingerprint,
                    date=str(day_before))
            if bwtype == 'Read':
                y_start, y_end, y_list = day_before_hist.read
            elif bwtype == 'Written':
                y_start, y_end, y_list = day_before_hist.written
            y_list.extend([0] * (95 - y_end))
            y_list[0:0] = ([0] * y_start)

        except Bwhist.DoesNotExist:
            y_list = ([0] * 96)
        tr_list[0:0] = y_list[(-1 * to_fill):]

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    # Return bytes per second, not total bandwidth for 15 minutes
    bps = map(lambda x: x / (15 * 60), tr_list)
    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = "%0*d:%0*d" % (2, to_add_date.hour,
                                    2, to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    # Draw the graph and give the graph a light shade underneath it
    ax.plot(dates, bps, color=color)
    ax.fill_between(dates, 0, bps, color=shade)

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance
    ax.set_ylim(ymin=0)

    # Don't use scientific notation
    ax.yaxis.major.formatter.set_scientific(False)

    # Format the y-tick labels with the desired font weight and size
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Average Bandwidth " + bwtype + " History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight=FONT_WEIGHT)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

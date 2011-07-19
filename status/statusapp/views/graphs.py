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
from statusapp.models import Statusentry, Bwhist, TotalBandwidth, \
        NetworkSize
from custom.aggregate import CountCase
from helpers import draw_bar_graph, draw_line_graph


DEFAULT_PARAMS = {'WIDTH': 960, 'HEIGHT': 320, 'TOP_MARGIN': 25,
                  'BOTTOM_MARGIN': 19, 'LEFT_MARGIN': 38,
                  'RIGHT_MARGIN': 5, 'X_FONT_SIZE': '8',
                  'Y_FONT_SIZE': '9', 'LABEL_FONT_SIZE': '8',
                  'LABEL_FLOAT': 3, 'LABEL_ROT': 'horizontal',
                  'FONT_WEIGHT': 'bold', 'BAR_WIDTH': 0.5,
                  'COLOR': '#66CD00', 'TITLE': ''}
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


@cache_page(60 * 5)
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

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va).extra(
                            select={'geoip': 'geoip_lookup(address)'})

    country_map = {}

    for entry in statusentries:
        # 'geoip' is a string, where the second and third characters
        # make the country code.
        if entry.geoip is None:
            country = '??'
        else:
            country = entry.geoip[1:3]
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 5)
def exitbycountrycode(request):
    """
    Return a graph representing the number of exit routers
    by country code.

    @rtype: HttpResponse
    @return: A graph representing the number of exit routers by country
        code as an HttpResponse object.
    """
    params = copy(DEFAULT_PARAMS)
    params['LABEL_ROT'] = 'vertical'
    params['TITLE'] = 'Number of Exit Routers by Country Code'

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va, isexit=1).extra(
                            select={'geoip': 'geoip_lookup(address)'})

    country_map = {}

    for entry in statusentries:
        # 'geoip' is a string, where the second and third characters
        # make the country code.
        if entry.geoip is None:
            country = '??'
        else:
            country = entry.geoip[1:3]
        if country in country_map:
            country_map[country] += 1
        else:
            country_map[country] = 1

    keys = sorted(country_map)
    num_params = len(keys)
    xs = range(num_params)
    ys = [country_map[key] for key in keys]

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 5)
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

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va)

    uptime_map = {}

    # This step is very inefficient; a custom SUM(CASE WHERE...
    # should be written.
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

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 5)
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

    # Define the ranges for the graph, a list of 2-tuples of ints.
    RANGES = [(0, 10), (11, 20), (21, 50), (51, 100), (101, 500),
              (501, 1000), (1001, 2000), (2001, 3000), (3001, 5000)]

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va)

    bw_map = {}
    excess = RANGES[-1][1] + 1

    for rng in RANGES:
        bw_map[rng] = 0
    bw_map[excess] = 0

    for entry in statusentries:
        kbps = entry.descriptorid.bandwidthobserved / 1024

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

    return draw_bar_graph(xs, ys, labels, params)


@cache_page(60 * 5)
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

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va)

    platform_map = {}
    keys = ['Linux', 'Windows', 'FreeBSD', 'Darwin', 'OpenBSD',
            'NetBSD', 'SunOS']
    for platform in keys:
        platform_map[platform] = 0

    platform_map['Unknown'] = 0

    # Inefficient for the same reason that the observed bandwidth
    # graph is inefficient; a custom SUM(CASE WHERE... should be
    # necessary here.
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

    return draw_bar_graph(xs, ys, keys, params)


@cache_page(60 * 5)
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

    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(validafter=last_va)

    total = statusentries.count()
    counts = Statusentry.objects.filter(validafter=last_va).aggregate(
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

    ys = []
    ys.append(total)
    for count in keys:
        ys.append(counts[count])

    return draw_bar_graph(xs, ys, labels, params)


cache_page(60 * 5)
def networktotalbw(request):
    """
    Return a graph representing the total bandwidth of the Tor network.

    @rtype: HttpResponse
    @return: A graph representing the total bandwidth of the
        Tor Network.
    """
    #TITLE = 'Tor Network Status'
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

    tbw_entries = list(TotalBandwidth.objects.all().order_by('-date')[:93])

    data_points = len(tbw_entries)
    xs = range(data_points)

    ys_bwobserved = []
    ys_bwburst = []
    ys_bwadvertised = []
    ys_bwavg = []

    for i in range(data_points - 1, -1, -1):
        tbw_today = tbw_entries[i]
        ys_bwobserved.append(tbw_today.bwobserved / float(1024**2))
        ys_bwburst.append(tbw_today.bwburst / float(1024**2))
        ys_bwadvertised.append(tbw_today.bwadvertised / float(1024**2))
        ys_bwavg.append(tbw_today.bwavg / float(1024**2))

    times = []
    start_date = tbw_entries[-1].date
    for i in range(0, data_points, 7):
        to_add_date = start_date + datetime.timedelta(days=(1 * i))
        to_add_str = "%s-%0*d" % (to_add_date.month,
                                  2, to_add_date.day)
        times.append(to_add_str)

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80

    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)

    # Draw bandwidth observed line
    ax1 = fig.add_subplot(111)
    #ax1.grid(color='#888888')

    # ax.plot(xs, ys_bwobserved, color='#66CD00',
    #         xs, ys_bwburst, color='#68228B',
    #         xs, ys_bwadvertised, color='#22688B',
    #         xs, ys_bwavg, color='#CD6600')
    observed_bw = ax1.plot(xs, ys_bwobserved, color='#68228B',
                           label='Observed Bandwidth')

    ax1.fill_between(xs, 0, ys_bwobserved, color='#DAC8E2')

    ax1.set_xlabel("Date (GMT)", fontsize='8', fontweight=FONT_WEIGHT)
    ax1.set_xticks(range(0, data_points, 7))
    ax1.set_xticklabels(times, fontsize=X_FONT_SIZE,
                        fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    ax1.set_ylabel("Bandwidth (MiB)",
                  fontsize='8', fontweight=FONT_WEIGHT)
    #ax1.set_yticks(range(0, 3001, 500))

    for tick in ax1.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    for tick in ax1.get_yticklabels():
        tick.set_color('#68228B')

    # Draw average relays running line
    # Assume that the dates in net_size are the same as in tbw_entries
    net_size = list(NetworkSize.objects.all().order_by('-date')[:93])

    ys = []
    for i in range(data_points - 1, -1, -1):
        ys.append(net_size[i].avg_running)

    ax2 = ax1.twinx()
    active_relays = ax2.plot(xs, ys, color='#66CD00',
                             label='Average Active Relays')

    ax2.set_xticks(range(0, data_points, 7))
    ax2.set_xticklabels(times, fontsize=X_FONT_SIZE,
                        fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    ax2.set_ylabel('Relays', fontsize='8', fontweight=FONT_WEIGHT)

    for tick in ax2.yaxis.get_major_ticks():
        tick.label2.set_fontsize(Y_FONT_SIZE)
        tick.label2.set_fontweight(FONT_WEIGHT)

    for tick in ax2.get_yticklabels():
        tick.set_color('#66CD00')

    # Label entire graph
    #ax1.set_title(TITLE, fontsize='12', fontweight=FONT_WEIGHT)
    fontparam = matplotlib.font_manager.FontProperties(
                size=8, weight='bold')

    # TODO: put both labels in one legend. How?
    ax1.legend(prop=fontparam, loc='lower left')
    ax2.legend(prop=fontparam, loc='lower right')

    # TODO: Make the grid work for both lines.
    # Set tick marks such that a grid applies to both lines.
    ax1.set_ylim(ymin=0)
    ax2.set_ylim(ymin=max((0, min(ys))))
    ax1.yaxis.set_major_locator(MaxNLocator(4))
    ax2.yaxis.set_major_locator(MaxNLocator(5))
    #ax1.grid(color='#888888')
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

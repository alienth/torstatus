"""
Views for statusapp that involve creating dynamic graphs.
"""
# Python-specific import statements -----------------------------------
from copy import copy

# Django-specific import statements -----------------------------------
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.views.decorators.cache import cache_page

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Bwhist
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

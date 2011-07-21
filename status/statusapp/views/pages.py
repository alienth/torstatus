"""
The pages module for TorStatus.

This module contains a single controller for each page type.
"""
# General python import statements ------------------------------------
import subprocess
import datetime
from socket import getfqdn

# Django-specific import statements -----------------------------------
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpRequest
from django.db.models import Max, Sum, Count
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor, Bwhist,\
        TotalBandwidth
from custom.aggregate import CountCase
from helpers import *
from display_helpers import *

# INIT Variables ------------------------------------------------------
CURRENT_COLUMNS = ["Country Code", "Router Name", "Bandwidth",
                   "Uptime", "IP", "Hostname", "Icons", "ORPort",
                   "DirPort", "BadExit", "Named", "Exit",
                   "Authority", "Fast", "Guard", "Stable",
                   "Running", "Valid", "V2Dir", "Platform",
                  ]
AVAILABLE_COLUMNS = ["Fingerprint", "LastDescriptorPublished",
                     "Contact", "BadDir",]
NOT_MOVABLE_COLUMNS = ["Named", "Exit", "Authority", "Fast", "Guard",
                       "Stable", "Running", "Valid", "V2Dir",
                       "Platform",]


def splash(request):
    """
    The splash page for the TorStatus website.
    """
    #TODO: CLEAN IF STATEMENT
    client_address = request.META['REMOTE_ADDR']
    template_values = {}
    if 'button' in request.GET:
        if request.GET['button'] == 'Search':
            # SEND STUFF TO THE INDEX PAGE
            template_values = { 'search_for': request.GET['searchValue'],
                              }
            return render_to_response('splash.html', template_values)
        elif request.GET['button'] == 'Advanced Search':
            return advanced_search(request)
    else:
        return render_to_response('splash.html', template_values)

"""
#@cache_page(60 * 15) #, key_prefix="index")
def index(request, sort_filter):
    
    Supply a dictionary to the index.html template consisting of a list
    of active relays.

    Currently, an "active relay" is a relay that has a status entry
    that was published in the last consensus.

    @type sort_filter: C{string}
    @param: A string that contains both the column that should be
        ordered by and the actual ordering (ascending/descending);
        the values are separated by '_'.

    @rtype: HttpResponse
    @return: A dictionary consisting of information about each router
        in the network as well as aggregate information about the
        network itself.
    
    # INITIAL QUERY ---------------------------------------------------
    # -----------------------------------------------------------------
    # Get the initial query and necessary aggregate values for the
    # routers in the last consensus.
    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(
                    validafter=last_va).extra(
                    select={'geoip':
                    'geoip_lookup(statusentry.address)'})\
                    .order_by('nickname')

    num_routers = statusentries.count()

    bw_total = TotalBandwidth.objects.all().order_by(
               '-date')[:1][0].bwobserved

    total_counts = statusentries.aggregate(
                   bandwidthavg=Sum('descriptorid__bandwidthavg'),
                   bandwidthburst=Sum('descriptorid__bandwidthburst'),
                   bandwidthobserved=Sum('descriptorid__bandwidthobserved'))
    # Convert from B/s to KB/s
    total_counts['bandwidthavg'] /= 1024
    total_counts['bandwidthburst'] /= 1024
    total_counts['bandwidthobserved'] /= 1024

    # USER QUERY MODIFICATIONS ----------------------------------------
    # -----------------------------------------------------------------
    current_columns = []
    if not ('currentColumns' in request.session):
        request.session['currentColumns'] = CURRENT_COLUMNS
    current_columns = request.session['currentColumns']

    query_options = {}
    if (request.GET):
        if ('resetQuery' in request.GET):
            if ('queryOptions' in request.session):
                del request.session['queryOptions']
        else:
            query_options = request.GET
            request.session['queryOptions'] = query_options
    if (not query_options and 'queryOptions' in request.session):
            query_options = request.session['queryOptions']

    if query_options:
        statusentries = filter_statusentries(
                statusentries, query_options)

    # TABLE SORTING ---------------------------------------------------
    # -----------------------------------------------------------------
    sort_order = ''
    order_column_name = ''
    if sort_filter:
        order_column_name, sort_order = sort_filter.split('_')
        options = ['nickname', 'fingerprint', 'geoip',
                   'bandwidthobserved', 'uptime', 'published',
                   'hostname', 'address', 'orport', 'dirport',
                   'isbaddirectory', 'isbadexit',]

        descriptorlist_options = ['uptime', 'contact',
                                  'bandwidthobserved']
        altered_column_name = order_column_name
        if altered_column_name in options:
            if altered_column_name in descriptorlist_options:
                altered_column_name = 'descriptorid__' + \
                        altered_column_name
            if sort_order == 'ascending':
                statusentries = statusentries.order_by(
                        altered_column_name)
            elif sort_order == 'descending':
                statusentries = statusentries.order_by(
                        '-' + altered_column_name)

    # USER QUERY AGGREGATE STATISTICS ---------------------------------
    # -----------------------------------------------------------------
    counts = statusentries.aggregate(
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
             isv2dir=CountCase('isv2dir', when=True),
             bandwidthavg=Sum('descriptorid__bandwidthavg'),
             bandwidthburst=Sum('descriptorid__bandwidthburst'),
             bandwidthobserved=Sum('descriptorid__bandwidthobserved'))
    # Convert from B/s to KB/s
    if counts['bandwidthavg']:
        counts['bandwidthavg'] /= 1024
    if counts['bandwidthburst']:
        counts['bandwidthburst'] /= 1024
    if counts['bandwidthobserved']:
        counts['bandwidthobserved'] /= 1024

    in_query = statusentries.count()

    bw_disp = TotalBandwidth.objects.all()\
              .order_by('-date')[:1][0].bwobserved

    client_address = request.META['REMOTE_ADDR']

    # GENERATE HTML: TABLE HEADERS ------------------------------------
    # -----------------------------------------------------------------
    html_table_headers, html_current_columns = generate_table_headers(
            current_columns, order_column_name, sort_order)

    # GENERATE HTML: TABLE ROWS ---------------------------------------
    # -----------------------------------------------------------------
    html_table_rows = generate_table_rows(statusentries, current_columns,
                                html_current_columns)

    # GENERATE HTML: ADVANCE QUERY ------------------------------------
    # -----------------------------------------------------------------
    html_query_list_options = generate_query_list_options(query_options)
    html_query_input_options = generate_query_input_options(query_options)

    # PAGINATION ------------------------------------------------------
    # -----------------------------------------------------------------
    paginator = Paginator(statusentries, 50) # Show 50 statusentries
                                             # per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request is out of range, deliver last page of results.
    try:
        statusentries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        statusentries = paginator.page(paginator.num_pages)

    template_values = {'relay_list': statusentries,
                       'client_address': client_address,
                       'num_routers': num_routers,
                       'in_query': in_query,
                       'exp_time': 900,
                       'counts': counts,
                       'total_counts': total_counts,
                       'bw_disp': bw_disp,
                       'bw_total': bw_total,
                       'queryOptions': query_options,
                       'htmlTableHeaders': html_table_headers,
                       'htmlCurrentColumns': html_current_columns,
                       'htmlRowCode': html_table_rows,
                       'htmlQueryListOptions': html_query_list_options,
                       'htmlQueryInputOptions': html_query_input_options,
                      }
    return render_to_response('index.html', template_values)
"""
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest
from django.db.models import Q, Max
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from statusapp.models import ActiveRelay

def index(request):
    """
    Supply a dictionary to the index.html template consisting of a list
    of active relays.

    Currently, an "active relay" is a relay that has a status entry
    that was published in the last consensus.

    @rtype: HttpResponse
    @return: A dictionary consisting of information about each router
        in the network as well as aggregate information about the
        network itself.
    """
    # Get all relays in last consensus
    last_validafter = ActiveRelay.objects.aggregate(
                      last=Max('validafter'))['last']
    active_relays = ActiveRelay.objects.filter(
                    validafter=last_validafter).order_by('nickname')

    basic_input = request.GET.get('search', '')

    if basic_input:
        active_relays = active_relays.filter(
                        Q(nickname__istartswith=basic_input) | \
                        Q(fingerprint__istartswith=basic_input) | \
                        Q(address__istartswith=basic_input))
    else:
        filter_params = _get_filter_params(request)
                        # Get this from request.get,
                        # make dict ('isexit': 1, etc)
        #col_prefs = _get_col_prefs(request)
                    # Get this from request.get, too - a LIST of STRING
                    # such that we can use as col headers and query
                    # filters... may also need mappings.
        order = _get_order(request)

        active_relays = active_relays.filter(
                        **filter_params).order_by(
                        order) # .values_list(*col_prefs)

    # If the search returns only one relay, go to the details page for
    # that relay.
    if active_relays.count() == 1:
        url = ''.join(('/details/', active_relays[0].fingerprint))
        return redirect(url)

    # Make sure paginated is an integer. If 0, then do not paginate.
    # Otherwise, paginate.
    try:
        all_relays = int(request.GET.get('all', '0'))
    except ValueError:
        all_relays = 0

    if not all_relays:
        # Make sure entries per page is an integer. If not, or
        # if no value is specified, make entries per page 50.
        try:
            per_page = int(request.GET.get('pp', 50))
        except ValueError:
            per_page = 50

        paginator = Paginator(active_relays, per_page)

        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        # If page request is out of range, deliver last
        # page of results.
        try:
            paged_relays = paginator.page(page)
        except (EmptyPage, InvalidPage):
            paged_relays = paginator.page(paginator.num_pages)
    else:
        paginator = Paginator(active_relays, active_relays.count())
        paged_relays = paginator.page(1)

    number_results = active_relays.count()
    template_values = {'paged_relays': paged_relays,
                       'number_results': number_results,
                       'current_columns': ('Country Code',
                            'Router Name', 'Bandwidth', 'Uptime', 'IP',
                            'Fingerprint', 'LastDescriptorPublished',
                            'Contact', 'BadDir', 'Icons', 'Exit',
                            'Authority', 'Fast', 'V2Dir', 'Platform',
                            'Stable', 'ORPort', 'DirPort', 'BadExit')}
    return render_to_response('index.html', template_values)


# TODO
def _get_filter_params(request):
    """
    Get the filter preferences provided by the user via the
    HttpRequest.

    @type request: HttpRequest
    @param request: The HttpRequest provided by the client
    @rtype: C{dict} of C{string} to C{string}
    @return: A dictionary mapping query parameters to user-supplied
        input.
    """
    return {}


# TODO
_DEFAULT_COL_PREFS = []
def _get_col_prefs(request):
    """
    Get the order on the columns and the columns themselves from the
    user via the HttpRequest.

    @type request: HttpRequest
    @param request: The HttpRequest provided by the client.
    @rtype: C{list} of C{string}
    @return: The column preferences specified by the client.
    """
    return _DEFAULT_COL_PREFS


_SORT_OPTIONS = set((
                'validafter',
                'nickname',
                'fingerprint',
                'address',
                'orport',
                'dirport',
                'isauthority',
                'isbadexit',
                'isbaddirectory',
                'isexit',
                'isfast',
                'isguard',
                'ishsdir',
                'isnamed',
                'isstable',
                'isrunning',
                'isunnamed',
                'isvalid',
                'isv2dir',
                'isv3dir',
                'descriptor',
                'published',
                'bandwidthavg',
                'bandwidthburst',
                'bandwidthobserved',
                'bandwidthkbps',
                'uptime',
                'uptimedays',
                'platform',
                'contact',
                'onionkey',
                'signingkey',
                'exitpolicy',
                'family',
                'country',
                'latitude',
                'longitude'
                ))
def _get_order(request):
    """
    Get the sorting parameter and order from the user via the
    HttpRequest.

    This function returns 'nickname' if no order is specified or if
    there is an error parsing the supplied information.

    @type request: HttpRequest
    @param request: The HttpRequest provided by the client.
    @rtype: C{string}
    @return: The sorting parameter and order as specified by the
        HttpRequest object.
    """
    if 'sortparam' in request.GET and 'sortparam' in _SORT_OPTIONS:
        param = request.GET.get('sortparam')
    else:
        param = 'nickname'

    order = request.GET.get('ord', '')
    if order != '-':
        order = ''

    return ''.join((order, param))

def details(request, fingerprint):
    """
    Supply the L{ActiveRelay} information associated with a
    relay with a given fingerprint to the details.html template.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router to display the
        details of.
    @rtype: HttpResponse
    @return: The L{ActiveRelay} information of the router.
    """
    poss_relay = ActiveRelay.objects.filter(
                 fingerprint=fingerprint).order_by('-validafter')[:1]

    if not poss_relay:
        return archive(HttpRequest(), fingerprint)
    relay = poss_relay[0]

    # Some clients may want to look up old relays. Create an attribute
    # to flag active and unactive relays.
    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    if last_va != relay.validafter:
        relay.active = False
    else:
        relay.active = True
        published = relay.published
        now = datetime.datetime.now()
        diff = now - published
        diff_sec = (diff.microseconds + (
                    diff.seconds + diff.days * 24 * 3600) * 10**6) \
                    / 10**6
        relay.adjuptime = relay.uptime + diff_sec

    relay.hostname = getfqdn(str(relay.address))

    template_values = {'relay': relay}
    return render_to_response('details.html', template_values)

"""
def details(request, fingerprint):
    
    Supply the L{Statusentry} and L{Geoipdb} objects associated with a
    relay with a given fingerprint to the details.html template.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router to display the
        details of.
    @rtype: HttpResponse
    @return: The L{Statusentry}, L{Descriptor}, and L{Geoipdb}
        information of the router.
    
    # The SQL function 'geoip_lookup' is used here, since greater than
    # and less than are incorrectly implemented for IPAddressFields.
    # [:1] is djangonese for 'LIMIT 1', and
    # [0] gets the object rather than the QuerySet.
    statusentry = Statusentry.objects.filter(
                  fingerprint=fingerprint).extra(
                  select={'geoip': 'geoip_lookup(address)'}).order_by(
                  '-validafter')[:1][0]

    descriptor = statusentry.descriptorid

    # Some clients may want to look up old relays. Create an attribute
    # to flag active and unactive relays.
    last_va = Statusentry.objects.aggregate(
              last=Max('validafter'))['last']

    if last_va != statusentry.validafter:
        statusentry.active = False
    else:
        statusentry.active = True

    # Get the country, latitude, and longitude from the geoip attribute
    statusentry.country, lat, lng = statusentry.geoip.strip(
                                    '()').split(',')
    statusentry.latitude = float(lat)
    statusentry.longitude = float(lng)

    # Get the correct uptime, assuming that the router is still running
    published = descriptor.published
    now = datetime.datetime.now()
    diff = now - published
    diff_sec = (diff.microseconds + (
                diff.seconds + diff.days * 24 * 3600) * 10**6) / 10**6
    descriptor.adjuptime = descriptor.uptime + diff_sec

    # Get information from the raw descriptor.
    raw_list = str(descriptor.rawdesc).split("\n")
    descriptor.onion_key = ''
    descriptor.signing_key = ''
    descriptor.exit_info = []
    descriptor.contact = ''
    descriptor.family = []
    i = 0
    while (i < len(raw_list)):
        if raw_list[i].startswith('onion-key'):
            descriptor.onion_key = '\n'.join(
                    raw_list[(i + 1):(i + 6)])
        elif raw_list[i].startswith('signing-key'):
            descriptor.signing_key = '\n'.join(
                    raw_list[(i + 1):(i + 6)])
        elif raw_list[i].startswith(('accept', 'reject')):
            descriptor.exit_info.append(raw_list[i])
        elif raw_list[i].startswith('contact'):
            descriptor.contact = raw_list[i][8:]
        elif raw_list[i].startswith('family'):
            descriptor.family = raw_list[i][7:].split()
        i += 1

    descriptor.hostname = getfqdn(str(statusentry.address))

    template_values = {'descriptor': descriptor, 'statusentry':
                       statusentry}
    return render_to_response('details.html', template_values)
"""

def whois(request, address):
    """
    Get WHOIS information for a given IP address.

    @see: U{http://docs.python.org/library/subprocess.html}

    @type address: C{string}
    @param address: The IP address to gather WHOIS information for.
    @rtype: HttpResponse
    @return: The WHOIS information of the L{address} as an HttpResponse.
    """
    if not is_ipaddress(address):
        error_msg = 'Unparsable IP address supplied.'
        template_values = {'whois': error_msg, 'address': address}
        return render_to_response('whois.html', template_values)

    proc = subprocess.Popen(["whois %s" % address],
                              stdout=subprocess.PIPE,
                              shell=True)

    whois, err = proc.communicate()

    template_values = {'whois': whois, 'address': address}
    return render_to_response('whois.html', template_values)


def exitnodequery(request):
    """
    Determine if an IP address is an active Tor server, and optionally
    see if the server's exit policy would permit it to exit to a given
    destination IP address and port.

    This method aims to provide meaningful information to the client in
    the case of unparsable input by returning both the information
    requested as well as the input that the client provided. If the
    information requested is not retrievable, this method is able to
    give a useful and informative error message by passing both the text
    input provided by the user as well as whether or not that text input
    was valid to the template.

    @rtype: HttpResponse
    @return: Information such as whether or not the IP address given is
        a router in the Tor network, whether or not that router would
        allow exiting to a given IP address and port, and other helpful
        information in the case of unparsable input.
    """
    # Given by the client
    source = ""
    dest_ip = ""
    dest_port = ""
    source_valid = False
    dest_ip_valid = False
    dest_port_valid = False

    # Get the source, dest_ip, and dest_port from the HttpRequest object
    # if they exist, and declare them valid if they are valid.
    source = get_if_exists(request, 'queryAddress')
    if (is_ipaddress(source)):
        source_valid = True

    dest_ip = get_if_exists(request, 'destinationAddress')
    if (is_ipaddress(dest_ip)):
        dest_ip_valid = True

    dest_port = get_if_exists(request, 'destinationPort')
    if (is_port(dest_port)):
        dest_port_valid = True

    # Some users may assume exiting on port 80. If a destination IP
    # address is given without a port, assume that the user means
    # port 80.
    if (dest_ip_valid == True and dest_port_valid == False):
        dest_port = "80"
        dest_port_valid = True

    # To render to response
    is_router = False
    router_fingerprint = ""
    router_nickname = ""
    exit_possible = False
    relays = []
    if (source_valid):

        # Don't search entries published over 24 hours
        # from the most recent entries.
        last_va = Statusentry.objects.aggregate(
                  last=Max('validafter'))['last']
        oldest_tolerable = last_va - datetime.timedelta(days=1)

        fingerprints = Statusentry.objects.filter(
                       address=source,
                       validafter__gte=oldest_tolerable).values(
                       'fingerprint').annotate(Count('fingerprint'))

        # Grouped by fingerprints, which are unique. If at least one
        # fingerprint is found, there is a match, so for each
        # fingerprint, get the fingerprint and nickname.
        if (fingerprints):
            is_router = True

            # For each entry, gather the nickname and fingerprint. If a
            # destination IP and port are defined, also find whether or
            # not the entries will allow exiting to the given
            # IP and port.
            for fp_entry in fingerprints:
                # Note that the trailing [:1] is djangonese for
                # "LIMIT 1", so this query should not be expensive.
                statusentry_set = Statusentry.objects.filter(
                                  fingerprint=fp_entry['fingerprint'],
                                  validafter__gte=(
                                  oldest_tolerable)).order_by(
                                  '-validafter')[:1]
                statusentry = statusentry_set[0]

                nickname = statusentry.nickname
                fingerprint = statusentry.fingerprint
                exit_possible = False

                # If the client also wants to test the relay's exit
                # policy, dest_ip and dest_port cannot be empty strings.
                if (dest_ip_valid and dest_port_valid):
                    router_exit_policy = get_exit_policy(
                                         statusentry.descriptorid.rawdesc)

                    # Search the exit policy information for a case in
                    # which the given IP is in a subnet defined in the
                    # exit policy information of a relay.
                    for policy_line in router_exit_policy:
                        condition, network_line = (policy_line.strip())\
                                                   .split(' ')
                        subnet, port_line = network_line.split(':')

                        # When the IP is in the given subnet, check to
                        # ensure that the given destination port is also
                        # in the port defined in the exit policy
                        # information. When a match is found, see if the
                        # condition is "accept" or "reject".
                        if (is_ip_in_subnet(dest_ip, subnet)):
                            if (port_match(dest_port, port_line)):
                                if (condition == 'accept'):
                                    exit_possible = True
                                else:
                                    exit_possible = False
                                break

                relays.append((nickname, fingerprint, exit_possible))

    template_values = {'is_router': is_router,
                       'relays': relays,
                       'dest_ip': dest_ip,
                       'dest_port': dest_port,
                       'source': source,
                       'source_valid': source_valid,
                       'dest_ip_valid': dest_ip_valid,
                       'dest_port_valid': dest_port_valid}
    return render_to_response('nodequery.html', template_values)

@cache_page(60 * 30)
def networkstatisticgraphs(request):
    """
    Render an HTML template to response.
    """
    # As this page is written now, each graph does it's own querying.
    # Either this structure should be fixed or the queries should be
    # cached.
    return render_to_response('statisticgraphs.html')


def display_options(request):
    """
    Let the user choose what columns should be displayed on the index
    page. This view makes use of the sessions in order to store two
    array-listobjects (currentColumns and availableColumns) in a
    "cookie" file so that the implementation of the "REMOVE", "ADD",
    "UP" and "DOWN" options from the page could be possible. It orders
    the two array-lists by using the user input, through a GET single
    selection HTML form.

    @param: request
    @return: renders to the page the currently selected columns, the
        available columns and the previous selection.
    """
    current_columns = []
    available_columns = []
    not_movable_columns = NOT_MOVABLE_COLUMNS

    if ('resetPreferences' in request.GET):
        del request.session['currentColumns']
        del request.session['availableColumns']

    if not ('currentColumns' in request.session and 'availableColumns'
            in request.session):
        request.session['currentColumns'] = CURRENT_COLUMNS
        request.session['availableColumns'] = AVAILABLE_COLUMNS
    current_columns = request.session['currentColumns']
    available_columns = request.session['availableColumns']

    column_lists = [current_columns, available_columns, '']
    if ('removeColumn' in request.GET and 'selected_removeColumn'
        in request.GET):
        column_lists = button_choice(request, 'removeColumn',
                      'selected_removeColumn', current_columns,
                      available_columns)
    elif ('addColumn' in request.GET and 'selected_addColumn'
          in request.GET):
        column_lists = button_choice(request, 'addColumn',
                'selected_addColumn', current_columns, available_columns)
    elif ('upButton' in request.GET and 'selected_removeColumn'
          in request.GET):
        if not(request.GET['selected_removeColumn'] in
               not_movable_columns):
            column_lists = button_choice(request, 'upButton',
                          'selected_removeColumn', current_columns,
                          available_columns)
    elif ('downButton' in request.GET and 'selected_removeColumn'
          in request.GET):
        if not(request.GET['selected_removeColumn'] in
               not_movable_columns):
            column_lists = button_choice(request, 'downButton',
                          'selected_removeColumn', current_columns,
                          available_columns)

    template_values = {'currentColumns': column_lists[0],
                       'availableColumns': column_lists[1],
                       'selectedEntry': column_lists[2]}

    return render_to_response('displayoptions.html', template_values)


def advanced_search(request):
    search_value = ''
    if request.GET and 'searchValue' in request.GET:
        search_value = request.GET['searchValue']
    
    sort_options_order = ADVANCED_SEARCH_DECLR['sort_options_order']
    sort_options = ADVANCED_SEARCH_DECLR['sort_options']
    
    search_options_fields_order = ADVANCED_SEARCH_DECLR[
                                    'search_options_fields_order']
    search_options_fields = ADVANCED_SEARCH_DECLR['search_options_fields']
                          
    search_options_booleans_order = ADVANCED_SEARCH_DECLR[
                                    'search_options_booleans_order']
    search_options_booleans = ADVANCED_SEARCH_DECLR['search_options_booleans']
                            
    filter_options_order = ADVANCED_SEARCH_DECLR['filter_options_order']
    filter_options = ADVANCED_SEARCH_DECLR['filter_options']
                           


    #Displayoptions method stuff
    current_columns = []
    available_columns = []
    not_movable_columns = NOT_MOVABLE_COLUMNS

    if ('resetPreferences' in request.GET):
        del request.session['currentColumns']
        del request.session['availableColumns']

    if not ('currentColumns' in request.session and 'availableColumns'
            in request.session):
        request.session['currentColumns'] = CURRENT_COLUMNS
        request.session['availableColumns'] = AVAILABLE_COLUMNS
    current_columns = request.session['currentColumns']
    available_columns = request.session['availableColumns']

    column_lists = [current_columns, available_columns, '']
    if ('removeColumn' in request.GET and 'selected_removeColumn'
        in request.GET):
        column_lists = button_choice(request, 'removeColumn',
                      'selected_removeColumn', current_columns,
                      available_columns)
    elif ('addColumn' in request.GET and 'selected_addColumn'
          in request.GET):
        column_lists = button_choice(request, 'addColumn',
                'selected_addColumn', current_columns, available_columns)
    elif ('upButton' in request.GET and 'selected_removeColumn'
          in request.GET):
        if not(request.GET['selected_removeColumn'] in
               not_movable_columns):
            column_lists = button_choice(request, 'upButton',
                          'selected_removeColumn', current_columns,
                          available_columns)
    elif ('downButton' in request.GET and 'selected_removeColumn'
          in request.GET):
        if not(request.GET['selected_removeColumn'] in
               not_movable_columns):
            column_lists = button_choice(request, 'downButton',
                          'selected_removeColumn', current_columns,
                          available_columns)

    template_values = {'searchValue': search_value,
                       'sortOptionsOrder': sort_options_order,
                       'sortOptions': sort_options,
                       'searchOptionsFieldsOrder': search_options_fields_order,
                       'searchOptionsFields': search_options_fields,
                       'searchOptionsBooleansOrder': search_options_booleans_order,
                       'searchOptionsBooleans': search_options_booleans,
                       'filterOptionsOrder': filter_options_order,
                       'filterOptions': filter_options,
                       'currentColumns': column_lists[0],
                       'availableColumns': column_lists[1],
                       'selectedEntry': column_lists[2]
                      }

    return render_to_response('advanced_search.html', template_values)

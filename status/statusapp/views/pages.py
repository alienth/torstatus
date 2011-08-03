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
from django.db.models import Q, Max, Sum, Count
from django.db import connection
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor, Bwhist,\
        TotalBandwidth, ActiveRelay
from custom.aggregate import CountCase
from helpers import *
from display_helpers import *

# INIT Variables ------------------------------------------------------
CURRENT_COLUMNS = ['Country Code', 'Router Name', 'Bandwidth',
                   'Uptime', 'IP', 'Icons', 'ORPort',
                   'DirPort', 'BadExit', 'Named', 'Exit',
                   'Authority', 'Fast', 'Guard', 'Hibernating',
                   'Stable', 'V2Dir', 'Platform']

AVAILABLE_COLUMNS = ['Fingerprint', 'LastDescriptorPublished',
                     'Contact', 'BadDir']

NOT_MOVABLE_COLUMNS = ['Named', 'Exit', 'Authority', 'Fast', 'Guard',
                       'Hibernating', 'Stable', 'V2Dir', 'Platform']

DISPLAYABLE_COLUMNS = set(('Country Code', 'Router Name', 'Bandwidth',
                            'Uptime', 'IP', 'Icons', 'ORPort',
                            'DirPort', 'BadExit', 'Fingerprint',
                            'LastDescriptorPublished', 'Contact',
                            'BadDir'))

def splash(request):
    """
    The splash page for the TorStatus website.

    @rtype: HttpResponse
    @return: the splash page rendered to html.
    """
    return render_to_response("splash.html")


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

    # See if the user wants to reset search and display preferences
    reset = request.GET.get('reset', '')
    if reset == 'True':
        search_session_reset(request)

    # Get all relays in last consensus
    last_validafter = ActiveRelay.objects.aggregate(
                      last=Max('validafter'))['last']
    active_relays = ActiveRelay.objects.filter(
                    validafter=last_validafter).order_by('nickname')

    # Get the order specified by session.request
    order = get_order(request)
    if order.startswith('-'):
        ascending_or_descending = 'ascending'
        order_param = order[1:]
    else:
        ascending_or_descending = 'descending'
        order_param = order

    # See if the user has defined a "basic search", i.e. if the
    # user has supplied a search term on the splash page
    basic_input = request.GET.get('search', '')

    # See also if the user has defined an "advanced search", i.e., if
    # the user has supplied a search term on the advanced search page
    advanced_input = get_filter_params(request)

    # If the user defines both basic search parameters as well as
    # advanced search parameters via a GET, use only the advanced
    # search parameters
    if basic_input and advanced_input:
        basic_input = ''

    # If the user has just defined a "basic search", save the
    # search parameter in the session and delete the advanced
    # search filters
    if basic_input:
        request.session['search'] = basic_input
        if 'filters' in request.session:
            del request.session['filters']

    # Otherwise, if the user has just defined an "advanced search",
    # save the advanced search parameters in the session and delete
    # the basic search parameter
    elif advanced_input:
        advanced_input = get_filter_params(request)
        if 'search' in request.session:
            del request.session['search']

    # If neither a basic search nor an advanced search was just
    # defined, get the search information from the session
    else:
        basic_input = request.session.get('search', '')
        advanced_input = request.session.get('filters', {})

    # We should never have both basic_input AND advanced_input
    # defined at this point.
    assert not (basic_input and advanced_input)

    # If basic search input has been supplied, search the beginnings
    # of all fingerprints, nicknames, and IPs in the last consensus
    # and return any matches
    if basic_input:
        active_relays = active_relays.filter(
                        Q(nickname__istartswith=basic_input) | \
                        Q(fingerprint__istartswith=basic_input) | \
                        Q(address__istartswith=basic_input)).\
                        order_by(order)

    # Otherwise, an advanced search may have been defined, so filter
    # all relays by the parameters given
    else:
        active_relays = active_relays.filter(
                        **advanced_input).order_by(order)

    num_results = active_relays.count()

    # If the search returns only one relay, go to the details page for
    # that relay.
    if active_relays.count() == 1:
        url = ''.join(('/details/', active_relays[0].fingerprint))
        return redirect(url)

    # TODO: Eventually give client the option to view all relays
    # on one page. The page needs to load faster before this
    # is possible.
    all_relays = request.session.get('all', 0)

    # If the user doesn't want to see all of the relays, then paginate
    # results.
    if not all_relays:
        # Make sure entries per page is an integer. If not, or
        # if no value is specified, make entries per page 50.
        per_page = request.session.get('perpage', 50)
        paginator = Paginator(active_relays, per_page)

        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        # If page request is out of range, deliver last
        # page of results.
        try:
            paged_relays = paginator.page(page)
        except (EmptyPage, InvalidPage):
            paged_relays = paginator.page(paginator.num_pages)
    # Display all relays on one page by making the page size as large
    # as the current result set
    else:
        paginator = Paginator(active_relays, num_results)
        paged_relays = paginator.page(1)

    # Convert the list of relays to a dictionary object
    paged_relays.object_list = gen_list_dict(paged_relays.object_list)

    # Get the current columns from the session. If no current columns
    # are defined, just use the default, CURRENT_COLUMNS
    current_columns = request.session.get(
                      'currentColumns', CURRENT_COLUMNS)
    request.session['currentColumns'] = current_columns

    template_values = {'paged_relays': paged_relays,
                       'current_columns': current_columns,
                       'displayable_columns': DISPLAYABLE_COLUMNS,
                       'not_columns': NOT_MOVABLE_COLUMNS,
                       'request': request,
                       'column_value_name': COLUMN_VALUE_NAME,
                       'icons_list': ICONS,
                       'number_of_results': num_results,
                       'ascending_or_descending':
                                ascending_or_descending,
                       'order_param': order_param,
                       'all': False}

    return render_to_response('index.html', template_values)


@cache_page(60 * 10)
def full_index(request):
    """
    Display all columns and routers available.

    @rtype: C{HttpResponse}
    @return: The full, unpaged list of all columns and relays.
    """
    last_validafter = ActiveRelay.objects.aggregate(
                      last=Max('validafter'))['last']
    active_relays = ActiveRelay.objects.filter(
                    validafter=last_validafter).order_by(
                    'nickname')

    num_results = active_relays.count()

    columns = ['Country Code', 'Router Name', 'Fingerprint',
               'Bandwidth', 'Uptime', 'IP', 'Icons', 'ORPort',
               'DirPort', 'Named', 'Exit', 'Authority', 'Fast',
               'Guard', 'Hibernating', 'Stable', 'V2Dir', 'Platform',
               'Contact', 'LastDescriptorPublished', 'BadDir',
               'BadExit']

    paginator = Paginator(active_relays, num_results)
    paged_relays = paginator.page(1)
    paged_relays.object_list = gen_list_dict(paged_relays.object_list)

    template_values = {'paged_relays': paged_relays,
                       'current_columns': columns,
                       'displayable_columns': DISPLAYABLE_COLUMNS,
                       'not_columns': NOT_MOVABLE_COLUMNS,
                       'request': request,
                       'column_value_name': COLUMN_VALUE_NAME,
                       'icons_list': ICONS,
                       'number_of_results': num_results,
                       'all': True}

    return render_to_response('index.html', template_values)


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
    # We'll let the client look up a relay as long as it is in the
    # ActiveRelay cache; it need not be in the last consensus
    poss_relay = ActiveRelay.objects.filter(
                 fingerprint=fingerprint).order_by('-validafter')[:1]

    # If no such relay exists, display a 404 page with an informative
    # debugging message.
    if not poss_relay:
        return render_to_response(
                '404.html',
                {'debug_message': ('The server could not find any ' +
                                   'recently active relay with a ' +
                                   'fingerprint of ' + fingerprint +
                                   '.')})

    # Otherwise, at least one entry for the relay exists, so get the
    # most recent entry for this relay
    relay = poss_relay[0]

    # Create an attribute, 'active', to flag active/unactive relays
    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    # A relay is "active" if it is in the last consensus
    if last_va != relay.validafter:
        relay.active = False
    else:
        relay.active = True

    # Not all relays will have descriptors, but if a relay has a
    # descriptor, its relay.descriptor value will not be null
    if relay.descriptor:
        relay.hasdescriptor = True
    else:
        relay.hasdescriptor = False

    # If the relay has a descriptor and the relay is active, calculate
    # the adjusted uptime
    if relay.hasdescriptor and relay.active:
        published = relay.published
        now = datetime.datetime.now()
        diff = now - published
        diff_sec = (diff.microseconds + (
                    diff.seconds + diff.days * 24 * 3600) * 10**6) \
                    / 10**6
        relay.adjuptime = relay.uptime + diff_sec

    # TODO: eventually, we'll want to find a way to add a hostname
    # attribute into the database instead of calculating it each time
    # the details page is requested. It might be of interest on the
    # index page as well.
    # NOTE: getfqdn returns the IP address itself if no hostname is
    # available, so there is no need to catch errors or null objects.
    relay.hostname = getfqdn(str(relay.address))

    # Generate a dictionary mapping labels to
    # values in a router details table
    relay_dict = gen_relay_dict(relay)

    # Generate an alphabetical list of flags
    flags_list = gen_flags_list(relay)

    # Generate a list of labels for which
    # information about the relay exists
    options_list = gen_options_list(relay)

    template_values = {'relay': relay,
                       'relay_dict': relay_dict,
                       'options_list': options_list,
                       'flags_list': flags_list,
                       }
    return render_to_response('details.html', template_values)


def whois(request, address):
    """
    Get WHOIS information for a given IP address.

    @see: U{http://docs.python.org/library/subprocess.html}

    @type address: C{string}
    @param address: The IP address to gather WHOIS information for.
    @rtype: HttpResponse
    @return: The WHOIS information of the L{address} as an HttpResponse.
    """
    # Make sure that the given IP address is in fact an IP address
    if is_ipaddress(address):
        # NOTE: Linux/Unix specific command; would break on windows.
        # TODO: Find a replacement for this command.
        proc = subprocess.Popen(["whois %s" % address],
                                  stdout=subprocess.PIPE,
                                  shell=True)
        whois = proc.communicate()[0]

    # If the given IP address is not a valid IP address, the whois
    # information cannot be looked up. Supply helpful debugging
    # information in this case.
    else:
        whois = 'Unparsable IP address supplied.'

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
    # if they exist, and declare them valid if they are valid
    source = request.GET.get('queryAddress', '').strip()
    if is_ipaddress(source): source_valid = True

    dest_ip = request.GET.get('destinationAddress', '').strip()
    if is_ipaddress(dest_ip): dest_ip_valid = True

    dest_port = request.GET.get('destinationPort', '').strip()
    if is_port(dest_port): dest_port_valid = True

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

        # Search only entries in the last consensus.
        last_va = ActiveRelay.objects.aggregate(
                  last=Max('validafter'))['last']

        fingerprints = ActiveRelay.objects.filter(
                       address=source, validafter=last_va).values(
                       'fingerprint').annotate(
                       Count('fingerprint'))

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
                relay = ActiveRelay.objects.filter(
                        fingerprint=fp_entry['fingerprint']).order_by(
                        '-validafter')[:1][0]

                nickname = relay.nickname
                fingerprint = relay.fingerprint
                exit_possible = False

                # If the client also wants to test the relay's exit
                # policy, dest_ip and dest_port cannot be empty strings
                if (dest_ip_valid and dest_port_valid):

                    # Search the exit policy information for a case in
                    # which the given IP is in a subnet defined in the
                    # exit policy information of a relay.
                    for policy_line in relay.exitpolicy:
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

                # Render a 'relays' list to response consisting only of
                # the relays' nickname, fingerprint, and whether or not
                # exiting is possible to the specified IP and port.
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
    return render_to_response('statisticgraphs.html')


# NOTE/TODO: When the index page loads faster, increase the upper bound
MAX_PP = 200
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
    debug_message = ''

    # If the user has specified a number of relays per page, save the
    # input in the session.
    if 'pp' in request.GET:

        # Ensure that the supplied information is an integer between 1
        # and MAX_PP, inclusive.
        try:
            supplied_pp = int(request.GET.get('pp', ''))
            assert 1 <= supplied_pp <= MAX_PP
            request.session['perpage'] = supplied_pp

        # Display a helpful debug_message in the case of unusable input
        except (ValueError, AssertionError):
            debug_message = 'Unable to set \"Relays Per Page\" to' + \
                            ' the given value.\nPlease enter an' + \
                            ' integer between 1 and ' + str(MAX_PP) + \
                            ', inclusive.'

    # Get the number of relays per page from the session, and if it
    # doesn't exist, make it 50 by default.
    current_pp = int(request.session.get('perpage', 50))

    current_columns = []
    available_columns = []
    not_movable_columns = NOT_MOVABLE_COLUMNS

    # If the user wants to reset column preferences, remove all
    # column information from the session
    if ('resetPreferences' in request.GET):
        if 'currentColumns' in request.session:
            del request.session['currentColumns']
        if 'availableColumns' in request.session:
            del request.session['availableColumns']

    # If no currentColumns and availableColumns are defined,
    # save the defaults in the session
    if not ('currentColumns' in request.session and 'availableColumns'
            in request.session):
        request.session['currentColumns'] = CURRENT_COLUMNS
        request.session['availableColumns'] = AVAILABLE_COLUMNS

    # Now there is guaranteed to be currentColumns and availableColumns
    # information in the session, so get it
    # Current columns
    curr = request.session['currentColumns']
    # Available columns
    avail = request.session['availableColumns']
    # Selected column/entry
    sel = ''

    # The user wants to remove a column
    if ('removeColumn' in request.GET and
        'selected_removeColumn' in request.GET):
        curr, avail, sel = button_choice(request, 'remove',
                           'selected_removeColumn', curr, avail)

    # The user wants to add a column
    elif ('addColumn' in request.GET and
          'selected_addColumn' in request.GET):
        curr, avail, sel = button_choice(request, 'add',
                           'selected_addColumn', curr, avail)

    # The user wants to move a column 'up' in the
    # list of current columns
    elif ('upButton' in request.GET and
          'selected_removeColumn' in request.GET and
          request.GET['selected_removeColumn'] not in not_movable_columns):
        curr, avail, sel = button_choice(request, 'up',
                           'selected_removeColumn', curr, avail)

    # The user wants to move a column 'down' in the
    # list of current columns
    elif ('downButton' in request.GET and
          'selected_removeColumn' in request.GET and
          request.GET['selected_removeColumn'] not in not_movable_columns):
        curr, avail, sel = button_choice(request, 'down',
                           'selected_removeColumn', curr, avail)

    template_values = {'currentColumns': curr,
                       'availableColumns': avail,
                       'selectedEntry': sel,
                       'current_pp': current_pp,
                       'debug_message': debug_message}

    return render_to_response('displayoptions.html', template_values)


def advanced_search(request):
    """
    The advanced search page for the TorStatus site.
    """
    template_values = {'sortOptionsOrder': SORT_OPTIONS_ORDER,
                       'sortOptions': SORT_OPTIONS,
                       'searchOptionsFieldsOrder': SEARCH_OPTIONS_FIELDS_ORDER,
                       'searchOptionsFields': SEARCH_OPTIONS_FIELDS,
                       'searchOptionsFieldsBooleans': SEARCH_OPTIONS_FIELDS_BOOLEANS,
                       'searchOptionsBooleansOrder':
                                                SEARCH_OPTIONS_BOOLEANS_ORDER,
                       'searchOptionsBooleans': SEARCH_OPTIONS_BOOLEANS,
                       'filterOptionsOrder': FILTER_OPTIONS_ORDER,
                       'filterOptions': FILTER_OPTIONS,
                      }

    return render_to_response('advanced_search.html', template_values)

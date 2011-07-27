"""
The pages module for TorStatus.

This module contains a single controller for each page type.
"""
# General python import statements ------------------------------------
import subprocess
import datetime
from socket import getfqdn
import re

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
                   'Stable', 'V2Dir', 'Platform',]
                   #'Hostname'

AVAILABLE_COLUMNS = ['Fingerprint', 'LastDescriptorPublished',
                     'Contact', 'BadDir',]
                 
NOT_MOVABLE_COLUMNS = ['Named', 'Exit', 'Authority', 'Fast', 'Guard',
                       'Hibernating', 'Stable', 'V2Dir', 'Platform',]
                
DISPLAYABLE_COLUMNS = set(('Country Code', 'Router Name', 'Bandwidth',
                            'Uptime', 'IP', 'Icons', 'ORPort', 'DirPort',
                            'BadExit', 'Fingerprint', 
                            'LastDescriptorPublished', 'Contact', 'BadDir'))


def splash(request):
    """
    The splash page for the TorStatus website.
    """
    return render_to_response("splash.html")


def index_reset(request):
    if 'filters' in request.session:
        del request.session['filters']
    if 'search' in request.session:
        del request.session['search']
    if 'sort_filter' in request.session:
        del request.session['sort_filter']

    return index(request, 'nickname_ascending')


"""
def get_order(sort_filter):

    sort_order = ''
    order_column_name = ''

    underscore_count = sort_filter.count('_')
    if not underscore_count == 1:
        return None, 'ascending'
    order_column_name, sort_order = sort_filter.split('_')
    options = ['nickname', 'fingerprint', 'contact',
                   'bandwidthkbps', 'uptime', 'country',
                   'address', 'orport', 'dirport',
                   'isbaddirectory', 'isbadexit',]

    if order_column_name in options:
        if sort_order == 'ascending':
            return order_column_name, 'descending'
        elif sort_order == 'descending':
            return '-' + order_column_name, 'ascending'
    else:
        return None, 'ascending'
"""


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
        request.session['search'] = basic_input
    elif 'search' in request.session:
        basic_input = request.session['search']

    if 'sortOrder' in request.GET and 'sortListing' in request.GET:
        request.session['order'] = get_order(request)
    elif 'order' not in request.session:
        request.session['order'] = 'nickname'

    order = request.session['order']

    if basic_input:
        if 'filters' in request.session:
            del request.session['filters']
        active_relays = active_relays.filter(
                        Q(nickname__istartswith=basic_input) | \
                        Q(fingerprint__istartswith=basic_input) | \
                        Q(address__istartswith=basic_input)).\
                        order_by(order)
    else:
        if 'search' in request.session:
            del request.session['search']
        filter_params = get_filter_params(request)
        active_relays = active_relays.filter(
                        **filter_params).order_by(order)


    num_results = active_relays.count()
    # If the search returns only one relay, go to the details page for
    # that relay.
    if active_relays.count() == 1:
        url = ''.join(('/details/', active_relays[0].fingerprint))
        return redirect(url)

    # Make sure paginated is an integer. If 0, then do not paginate.
    # Otherwise, paginate.

    all_relays = request.session.get('all', 0)

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
    else:

        paginator = Paginator(active_relays,
                              active_relays.count())
        paged_relays = paginator.page(1)

    paged_relays.object_list = gen_list_dict(paged_relays.object_list)

    current_columns = []
    if not ('currentColumns' in request.session):
        request.session['currentColumns'] = CURRENT_COLUMNS
    current_columns = request.session['currentColumns']

    template_values = {'paged_relays': paged_relays,
                       'current_columns': current_columns,
                       'displayable_columns': DISPLAYABLE_COLUMNS,
                       'not_columns': NOT_MOVABLE_COLUMNS,
                       'request': request,
                       'column_value_name': COLUMN_VALUE_NAME,
                       'icons_list': ICONS,
                       'number_of_results': num_results,
                      }
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
    poss_relay = ActiveRelay.objects.filter(
                 fingerprint=fingerprint).order_by('-validafter')[:1]

    if not poss_relay:
        return render_to_response(
                '404.html',
                {'debug_message': 'The server could not find any '
                                  'recently active relay with a '
                                  'fingerprint of ' + fingerprint + '.'})
    relay = poss_relay[0]

    # Some clients may want to look up old relays. Create an attribute
    # to flag active and unactive relays.
    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']

    if last_va != relay.validafter:
        relay.active = False
    else:
        relay.active = True

    # Not all relays will have descriptors, but if a relay has a
    # descriptor, its relay.descriptor value will not be null.
    if relay.descriptor:
        relay.hasdescriptor = True
        published = relay.published
        now = datetime.datetime.now()
        diff = now - published
        diff_sec = (diff.microseconds + (
                    diff.seconds + diff.days * 24 * 3600) * 10**6) \
                    / 10**6
        relay.adjuptime = relay.uptime + diff_sec
    else:
        relay.hasdescriptor = False

    relay.hostname = getfqdn(str(relay.address))
    
    relay_dict = gen_relay_dict(relay)                 
    flags_list = gen_flags_list(relay)
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
    if not is_ipaddress(address):
        error_msg = 'Unparsable IP address supplied.'
        template_values = {'whois': error_msg, 'address': address}
        return render_to_response('whois.html', template_values)

    proc = subprocess.Popen(["whois %s" % address],
                              stdout=subprocess.PIPE,
                              shell=True)

    whois = proc.communicate()[0]

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

        # Don't search entries published over 24 hours
        # from the most recent entries.
        last_va = ActiveRelay.objects.aggregate(
                  last=Max('validafter'))['last']

        fingerprints = ActiveRelay.objects.filter(
                       address=source).values(
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
                # policy, dest_ip and dest_port cannot be empty strings.
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
    if 'pp' in request.GET:
        # Ensure that the supplied information is an integer greater
        # than zero.
        try:
            supplied_pp = int(request.GET.get('pp', ''))
            if supplied_pp > 1:
                request.session['perpage'] = supplied_pp
        except ValueError:
            pass

    current_pp = int(request.session.get('perpage', 50))

    current_columns = []
    available_columns = []
    not_movable_columns = NOT_MOVABLE_COLUMNS

    if ('resetPreferences' in request.GET):
        if 'currentColumns' in request.session:
            del request.session['currentColumns']
        if 'availableColumns' in request.session:
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
                       'selectedEntry': column_lists[2],
                       'current_pp': current_pp}

    return render_to_response('displayoptions.html', template_values)


def advanced_search(request):

    if 'filters' in request.session:
        del request.session['filters']
    if 'search' in request.session:
        del request.session['search']

    search_value = request.GET.get('search', '')

    sort_options_order = ADVANCED_SEARCH_DECLR['sort_options_order']
    sort_options = ADVANCED_SEARCH_DECLR['sort_options']

    search_options_fields_order = ADVANCED_SEARCH_DECLR[
                                    'search_options_fields_order']
    search_options_fields = ADVANCED_SEARCH_DECLR['search_options_fields']
    search_options_fields_booleans = ADVANCED_SEARCH_DECLR[
                                    'search_options_fields_booleans']

    search_options_booleans_order = ADVANCED_SEARCH_DECLR[
                                    'search_options_booleans_order']
    search_options_booleans = ADVANCED_SEARCH_DECLR['search_options_booleans']

    filter_options_order = ADVANCED_SEARCH_DECLR['filter_options_order']
    filter_options = ADVANCED_SEARCH_DECLR['filter_options']

    template_values = {'search': search_value,
                       'sortOptionsOrder': sort_options_order,
                       'sortOptions': sort_options,
                       'searchOptionsFieldsOrder': search_options_fields_order,
                       'searchOptionsFields': search_options_fields,
                       'searchOptionsFieldsBooleans':
                                                search_options_fields_booleans,
                       'searchOptionsBooleansOrder':
                                                search_options_booleans_order,
                       'searchOptionsBooleans': search_options_booleans,
                       'filterOptionsOrder': filter_options_order,
                       'filterOptions': filter_options,
                      }

    return render_to_response('advanced_search.html', template_values)

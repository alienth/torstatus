"""
The views module for TorStatus.

Django is idiosyncratic in that it names controllers 'views'; models
are still models and views are called templates. This module contains a
single controller for each page type.
"""
# General python import statements ------------------------------------
import subprocess
import datetime

# Django-specific import statements -----------------------------------
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest
from django.db.models import Max, Sum, Count

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor, Bwhist,\
        TotalBandwidth
from custom.aggregate import CountCase
from helpers import * 


# INIT Variables ------------------------------------------------------
CURRENT_COLUMNS = ["Country Code", "Router Name", "Bandwidth",
                   "Uptime", "IP", "Hostname", "Icons", "ORPort",
                   "DirPort", "BadExit", "Named", "Exit",
                   "Authority", "Fast", "Guard", "Stable",
                   "Running", "Valid", "V2Dir", "Platform",
                   "Hibernating"]
AVAILABLE_COLUMNS = ["Fingerprint", "LastDescriptorPublished",
                     "Contact", "BadDir"]
NOT_MOVABLE_COLUMNS = ["Named", "Exit", "Authority", "Fast", "Guard",
                       "Stable", "Running", "Valid", "V2Dir",
                       "Platform", "Hibernating"]

# TODO: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
#@cache_page(60 * 15) # Cache is turned off for development,
                      # but it works.


def index(request):
    """
    Supply a dictionary to the index.html template consisting of a list
    of active relays.

    Currently, an "active relay" is a relay that has a status entry
    that was published in the last consensus.

    @rtype: HttpRequest
    @return: A dictionary consisting of information about each router
        in the network as well as aggregate information about the
        network itself.
    """
    # INITIAL QUERY ---------------------------------------------------
    # -----------------------------------------------------------------
    # Get the initial query and necessary aggregate values for the
    # routers in the last consensus.
    last_va = Statusentry.objects.aggregate(\
            last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(\
                    validafter=last_va)\
                    .extra(select={'geoip':
                    'geoip_lookup(statusentry.address)'})\
                    .order_by('nickname')

    num_routers = statusentries.count()

    bw_total = TotalBandwidth.objects.all()\
               .order_by('-date')[:1][0].bwobserved

    total_counts = statusentries.aggregate(\
                   bandwidthavg=Sum('descriptorid__bandwidthavg'),
                   bandwidthburst=Sum('descriptorid__bandwidthburst'),
                   bandwidthobserved=Sum('descriptorid__bandwidthobserved'))

    # USER QUERY MODIFICATIONS ----------------------------------------
    # -----------------------------------------------------------------
    currentColumns = []
    if not ('currentColumns' in request.session):
        currentColumns = CURRENT_COLUMNS
        request.session['currentColumns'] = currentColumns
    else:
        currentColumns = request.session['currentColumns']

    queryOptions = {}
    if (request.GET):
        if ('resetQuery' in request.GET):
            if ('queryOptions' in request.session):
                del request.session['queryOptions']
        else:
            queryOptions = request.GET
            request.session['queryOptions'] = queryOptions
    if (not queryOptions and 'queryOptions' in request.session):
            queryOptions = request.session['queryOptions']

    if queryOptions:
        if queryOptions['isauthority'] == 'yes':
            statusentries = statusentries.filter(isauthority=1)
        elif queryOptions['isauthority'] == 'no':
            statusentries = statusentries.filter(isauthority=0)
        if queryOptions['isbaddirectory'] == 'yes':
            statusentries = statusentries.filter(isbaddirectory=1)
        elif queryOptions['isbaddirectory'] == 'no':
            statusentries = statusentries.filter(isbaddirectory=0)
        if queryOptions['isbadexit'] == 'yes':
            statusentries = statusentries.filter(isbadexit=1)
        elif queryOptions['isbadexit'] == 'no':
            statusentries = statusentries.filter(isbadexit=0)
        if queryOptions['isexit'] == 'yes':
            statusentries = statusentries.filter(isexit=1)
        elif queryOptions['isexit'] == 'no':
            statusentries = statusentries.filter(isexit=0)
        if queryOptions['isfast'] == 'yes':
            statusentries = statusentries.filter(isfast=1)
        elif queryOptions['isfast'] == 'no':
            statusentries = statusentries.filter(isfast=0)
        if queryOptions['isguard'] == 'yes':
            statusentries = statusentries.filter(isguard=1)
        elif queryOptions['isguard'] == 'no':
            statusentries = statusentries.filter(isguard=0)
        '''
        if queryOptions['ishibernating'] == 'yes':
            statusentries = statusentries.filter(ishibernating=1)
        elif queryOptions['ishibernating'] == 'no':
            statusentries = statusentries.filter(ishibernating=0)
        '''
        if queryOptions['isnamed'] == 'yes':
            statusentries = statusentries.filter(isnamed=1)
        elif queryOptions['isnamed'] == 'no':
            statusentries = statusentries.filter(isnamed=0)
        if queryOptions['isstable'] == 'yes':
            statusentries = statusentries.filter(isstable=1)
        elif queryOptions['isstable'] == 'no':
            statusentries = statusentries.filter(isstable=0)
        if queryOptions['isrunning'] == 'yes':
            statusentries = statusentries.filter(isrunning=1)
        elif queryOptions['isrunning'] == 'no':
            statusentries = statusentries.filter(isrunning=0)
        if queryOptions['isvalid'] == 'yes':
            statusentries = statusentries.filter(isvalid=1)
        elif queryOptions['isvalid'] == 'no':
            statusentries = statusentries.filter(isvalid=0)
        if queryOptions['isv2dir'] == 'yes':
            statusentries = statusentries.filter(isv2dir=1)
        elif queryOptions['isv2dir'] == 'no':
            statusentries = statusentries.filter(isv2dir=0)

       ###################################
       #
       # FINISH THIS ----> 
       #
       ################################### 
        if queryOptions['searchValue'] != "":
            # IDEA TO AVOID MULTIPLE, REDUNDANT, IF STATEMENTS
            #criteriaDict = {'fingerprint': fingerprint, 'nickname': nickname,
            #                'countrycode': geoip[1:3], }
            value = queryOptions['searchValue']
            criteria = queryOptions['criteria']
            logic = queryOptions['boolLogic']
            
            if criteria == 'fingerprint':
                if logic == 'equals':
                    statusentries = statusentries.filter(fingerprint=value)
                elif logic == 'contains':
                    statusentries = statusentries.filter(fingerprint__contains=value)
                elif logic == 'less':
                    statusentries = statusentries.filter(fingerprint__lt=value)
                elif logic == 'greater':
                    statusentries = statusentries.filter(fingerprint__gt=value)
            elif criteria == 'nickname':
                if logic == 'equals':
                    statusentries = statusentries.filter(nickname=value)
                elif logic == 'contains':
                    statusentries = statusentries.filter(nickname__contains=value)
                elif logic == 'less':
                    statusentries = statusentries.filter(nickname__lt=value)
                elif logic == 'greater':
                    statusentries = statusentries.filter(nickname__gt=value)
        
        sortOptions = ['nickname', 'fingerprint', 'geoip',
                       'bandwidth', 'uptime', 'published',
                       'hostname', 'address', 'orport', 'dirport',
                       'platform', 'contact', 'isauthority', 
                       'isbaddirectory', 'isbadexit', 'isexit',
                       'isfast', 'isguard', 'ishibernating', 
                       'isnamed', 'isstable', 'isrunning', 
                       'isvalid', 'isv2dir']
        descriptorList = ['platform', 'uptime', 'contact'] 
        selectedOption = queryOptions['sortListings']
        if selectedOption in sortOptions:
            if selectedOption in descriptorList:
                selectedOption = 'descriptorid__' + selectedOption
            if queryOptions['sortOrder'] == 'ascending':
                statusentries = statusentries.order_by(selectedOption)
            elif queryOptions['sortOrder'] == 'descending':
                statusentries = statusentries.order_by('-' + selectedOption)
                
        
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

    bw_disp = TotalBandwidth.objects.all()\
              .order_by('-date')[:1][0].bwobserved

    in_query = statusentries.count()
    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': statusentries,
                       'client_address': client_address,
                       'num_routers': num_routers,
                       'in_query': in_query,
                       'exp_time': 900,
                       'counts': counts,
                       'total_counts': total_counts,
                       'bw_disp': bw_disp,
                       'bw_total': bw_total,
                       'currentColumns': currentColumns,
                       'queryOptions': queryOptions}
    return render_to_response('index.html', template_values)


def details(request, fingerprint):
    """
    Supply the L{Statusentry} and L{Geoipdb} objects associated with a
    relay with a given fingerprint to the details.html template.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router to display the
        details of.
    @rtype: HttpResponse
    @return: The L{Statusentry}, L{Descriptor}, and L{Geoipdb}
        information of the router.
    """
    # The SQL function 'geoip_lookup' is used here, since greater than
    # and less than are incorrectly implemented for IPAddressFields.
    # [:1] is djangonese for 'LIMIT 1', and
    # [0] gets the object rather than the QuerySet.
    
    statusentry = Statusentry.objects.filter(fingerprint=fingerprint)\
                  .extra(select={'geoip': 'geoip_lookup(address)'})\
                  .order_by('-validafter')[:1][0]

    descriptor = statusentry.descriptorid
    template_values = {'descriptor': descriptor, 'statusentry': statusentry}
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

    whois, err = proc.communicate()

    template_values = {'whois': whois, 'address': address}
    return render_to_response('whois.html', template_values)


def exitnodequery(request):
    # TODO: See code reviews from 21 June
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
        last_va = Statusentry.objects.aggregate(\
                  last=Max('validafter'))['last']
        oldest_tolerable = last_va - datetime.timedelta(days=1)

        fingerprints = Statusentry.objects.filter(\
                       address=source,
                       validafter__gte=oldest_tolerable)\
                       .values('fingerprint')\
                       .annotate(Count('fingerprint'))

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
                statusentry_set = Statusentry.objects.filter(\
                                  fingerprint=fp_entry['fingerprint'], \
                                  validafter__gte=(oldest_tolerable))\
                                  .order_by('-validafter')[:1]
                statusentry = statusentry_set[0]

                nickname = statusentry.nickname
                fingerprint = statusentry.fingerprint
                exit_possible = False

                # If the client also wants to test the relay's exit
                # policy, dest_ip and dest_port cannot be empty strings.
                if (dest_ip_valid and dest_port_valid):
                    router_exit_policy = get_exit_policy(\
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


def networkstatisticgraphs(request):
    """
    Render an HTML template to response.
    """
    # As this page is written now, each graph does it's own querying.
    # Either this structure should be fixed or the queries should be
    # cached.
    return render_to_response('statisticgraphs.html')


def columnpreferences(request):
    '''
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
    '''
    currentColumns = []
    availableColumns = []
    notMovableColumns = NOT_MOVABLE_COLUMNS

    if ('resetPreferences' in request.GET):
        del request.session['currentColumns']
        del request.session['availableColumns']

    if not ('currentColumns' in request.session and 'availableColumns' \
            in request.session):
        currentColumns = CURRENT_COLUMNS
        availableColumns = AVAILABLE_COLUMNS
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns
    else:
        currentColumns = request.session['currentColumns']
        availableColumns = request.session['availableColumns']

    columnLists = [currentColumns, availableColumns, '']
    if ('removeColumn' in request.GET and 'selected_removeColumn' \
        in request.GET):
        columnLists = buttonChoice(request, 'removeColumn',
                      'selected_removeColumn', currentColumns,
                      availableColumns)
    elif ('addColumn' in request.GET and 'selected_addColumn' \
          in request.GET):
        columnLists = buttonChoice(request, 'addColumn',
                'selected_addColumn', currentColumns, availableColumns)
    elif ('upButton' in request.GET and 'selected_removeColumn' \
          in request.GET):
        if not(request.GET['selected_removeColumn'] in \
               notMovableColumns):
            columnLists = buttonChoice(request, 'upButton', \
                          'selected_removeColumn', currentColumns,
                          availableColumns)
    elif ('downButton' in request.GET and 'selected_removeColumn' \
          in request.GET):
        if not(request.GET['selected_removeColumn'] in \
               notMovableColumns):
            columnLists = buttonChoice(request, 'downButton', \
                          'selected_removeColumn', currentColumns,
                          availableColumns)

    template_values = {'currentColumns': columnLists[0],
                       'availableColumns': columnLists[1],
                       'selectedEntry': columnLists[2]}

    return render_to_response('columnpreferences.html', template_values)

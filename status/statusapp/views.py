"""
The views module for TorStatus.

Django is idiosyncratic in that it names controllers 'views'; models
are still models and views are called templates. This module contains a
single controller for each page type.
"""
import time
import datetime
import csv
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest, Http404
from django.db import connection
import csv
from statusapp.models import Statusentry, Descriptor, Bwhist, Geoipdb, TotalBandwidth
import datetime
import time
from django.db.models import Max, Sum
from custom.aggregate import CountCase


# TODO: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
#@cache_page(60 * 15) # Cache is turned off for development,
                      # but it works.


def index(request):
    """
    Supply a dictionary to the index.html template consisting of keys
    equivalent to columns in the statusentry and descriptor tables in the
    database. Querying the database is done with raw SQL. This needs 
    to be fixed. Also, returning an array-list of the column names to
    be displayed.
    """   
    
    currentColumns = []
    if not ('currentColumns' in request.session):
        currentColumns = ["Country Code", "Uptime", "Hostname", "ORPort", "DirPort", "IP", \
                    "Exit", "Authority", "Fast", "Guard", "Named", "Stable", "Running", "Valid", \
                    "Bandwidth", "V2Dir", "Platform", "Hibernating", "BadExit",]
        request.session['currentColumns'] = currentColumns
    else:
        currentColumns = request.session['currentColumns']

    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    a = Statusentry.objects.filter(validafter=last_va).extra(select={'geoip': 'geoip_lookup(address)'}).order_by('nickname')

    counts = a.aggregate(
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
    
    #MIGHT WORKS BUT DOESN'T SORT BY CERTAIN PARAMATERS SUCH AS COUNTRY
    #if 'sortListings' in request.GET:
    #    a = Statusentry.objects.filter(validafter=last_va).extra(select={'geoip': 'geoip_lookup(address)'}).order_by(request.GET['sortListings'])
    #else:
    #    a = Statusentry.objects.filter(validafter=last_va).extra(select={'geoip': 'geoip_lookup(address)'}).order_by('nickname')
    
    #############################################################
    
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
            a = a.filter(isauthority=1)
        elif queryOptions['isauthority'] == 'no': 
            a = a.filter(isauthority=0)
        if queryOptions['isbaddirectory'] == 'yes':
            a = a.filter(isbaddirectory=1)
        elif queryOptions['isbaddirectory'] == 'no':  
            a = a.filter(isbaddirectory=0)
        if queryOptions['isbadexit'] == 'yes':
            a = a.filter(isbadexit=1)
        elif queryOptions['isbadexit'] == 'no': 
            a = a.filter(isbadexit=0)
        if queryOptions['isexit'] == 'yes':
            a = a.filter(isexit=1)
        elif queryOptions['isexit'] == 'no': 
            a = a.filter(isexit=0)
        '''
        if queryOptions['ishibernating'] == 'yes':
            a = a.filter(ishibernating=1)
        elif queryOptions['ishibernating'] == 'no': 
            a = a.filter(ishibernating=0)
        '''
        if queryOptions['isnamed'] == 'yes':
            a = a.filter(isnamed=1)
        elif queryOptions['isnamed'] == 'no': 
            a = a.filter(isnamed=0)
        if queryOptions['isstable'] == 'yes':
            a = a.filter(isstable=1)
        elif queryOptions['isstable'] == 'no': 
            a = a.filter(isstable=0)
        if queryOptions['isrunning'] == 'yes':
            a = a.filter(isrunning=1)
        elif queryOptions['isrunning'] == 'no': 
            a = a.filter(isrunning=0)
        if queryOptions['isvalid'] == 'yes':
            a = a.filter(isvalid=1)
        elif queryOptions['isvalid'] == 'no': 
            a = a.filter(isvalid=0)
        if queryOptions['isv2dir'] == 'yes':
            a = a.filter(isv2dir=1)
        elif queryOptions['isv2dir'] == 'no': 
            a = a.filter(isv2dir=0)
    #############################################################

    total_bw = TotalBandwidth.objects.all().order_by('-date')[:1][0].bwobserved
    num_routers = a.count()
    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': a, 'client_address': client_address, 'num_routers': num_routers, 'exp_time': 900,
            'currentColumns': currentColumns, 'queryOptions': queryOptions, 'counts': counts, 'total_bw': total_bw}
    return render_to_response('index.html', template_values)

def details(request, fingerprint):
    
    #This block gets the specific descriptor and statusentry that the client asked for

    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    a = Statusentry.objects.filter(validafter=last_va).extra(select={'geoip': 'geoip_lookup(address)'}).order_by('nickname')
    entry = a.filter(fingerprint = fingerprint).order_by('validafter')[0]
    descriptor = entry.descriptorid
    template_values = {'descriptor': descriptor, 'statusentry': entry}
    return render_to_response('details.html', template_values)

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
    source = _get_if_exists(request, 'queryAddress')
    if (_is_ipaddress(source)):
        source_valid = True

    dest_ip = _get_if_exists(request, 'destinationAddress')
    if (_is_ipaddress(dest_ip)):
        dest_ip_valid = True

    dest_port = _get_if_exists(request, 'destinationPort')
    if (_is_port(dest_port)):
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
        from django.db.models import Max, Count

        # Don't search entries published over 24 hours
        # from the most recent entries.
        last_va = Statusentry.objects.aggregate(\
                last=Max('validafter'))['last']
        oldest_tolerable = last_va - datetime.timedelta(days=1)

        fingerprints = Statusentry.objects.filter(address=source, \
                validafter__gte=oldest_tolerable).values('fingerprint')\
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
                    router_exit_policy = _get_exit_policy(statusentry.\
                            descriptorid.rawdesc)

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
                        if (_is_ip_in_subnet(dest_ip, subnet)):
                            if (_port_match(dest_port, port_line)):
                                if (condition == 'accept'):
                                    exit_possible = True
                                else:
                                    exit_possible = False
                                break

                relays.append((nickname, fingerprint, exit_possible))

    template_values = {'is_router': is_router, 'relays': relays,
            'dest_ip': dest_ip, 'dest_port': dest_port, 'source':
            source, 'source_valid': source_valid, 'dest_ip_valid':
            dest_ip_valid, 'dest_port_valid': dest_port_valid}
    return render_to_response('nodequery.html', template_values)

def unruly_passengers_csv(request):
    # For now, this function is just a placeholder. We're using this to see
    # if we can understand the csv module.
    """
    """
    UNRULY_PASSENGERS = [146,184,235,200,226,251,299,273,281,304,203]
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test_data.csv'

    # Create the CSV writer using the HttpResponse as the "file."
    writer = csv.writer(response)
    writer.writerow(['Year', 'Unruly Airline Passengers'])
    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
        writer.writerow([year, num])

    return response

def networkstatisticgraphs(request):
    #TODO
    # For now, this function is just a placeholder.

    variables = "TEMP STRING"
    template_values = {'variables': variables}
    return render_to_response('nodequery.html', template_values)


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
    #
    #NOTE: The view is currently using sessions and it's storing the session
    #   into a file in the folder tmp/ from the status/ folder.
    #
    #TODO: Give the Session ID a reasonable "life-time" - so it wouldn't stay
    #   on the system forever (or until it is manually deleted).
    #TODO: Integrate the array-list into the index page so it will actually
    #   display only the desired information.
    #TODO: Clean the code of unnecessary pieces.
    #

    currentColumns = []
    availableColumns = []
    
    if ('resetPreferences' in request.GET):
        del request.session['currentColumns']
        del request.session['availableColumns']

    if not ('currentColumns' in request.session and 'availableColumns' in request.session):
        currentColumns = ["Country Code", "Uptime", "Hostname", "ORPort", "DirPort", "IP", \
                    "Exit", "Authority", "Fast", "Guard", "Named", "Stable", "Running", "Valid", \
                    "Bandwidth", "V2Dir", "Platform", "Hibernating", "BadExit",]
        availableColumns = ["Fingerprint", "LastDescriptorPublished", "Contact", "BadDir"]
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns
    else:
        currentColumns = request.session['currentColumns']
        availableColumns = request.session['availableColumns']
    
    columnLists = [currentColumns, availableColumns, '']
    if ('removeColumn' in request.GET and 'selected_removeColumn' in request.GET):
        columnLists = _buttonChoice(request, 'removeColumn', 'selected_removeColumn', currentColumns, availableColumns)
    elif ('addColumn' in request.GET and 'selected_addColumn' in request.GET):
        columnLists = _buttonChoice(request, 'addColumn', 'selected_addColumn', currentColumns, availableColumns)
    elif ('upButton' in request.GET and 'selected_removeColumn' in request.GET):
        columnLists = _buttonChoice(request, 'upButton', 'selected_removeColumn', currentColumns, availableColumns)
    elif ('downButton' in request.GET and 'selected_removeColumn' in request.GET):
        columnLists = _buttonChoice(request, 'downButton', 'selected_removeColumn', currentColumns, availableColumns)
    
    template_values = {'currentColumns': columnLists[0], 'availableColumns': columnLists[1], \
                    'selectedEntry': columnLists[2]}
    
    return render_to_response('columnpreferences.html', template_values)

def _buttonChoice(request, button, field, currentColumns, availableColumns): 
    '''
    Helper function that manages the changes in the column preferences array-lists.
    @see: columnpreferences
    @rtype: list(list(int), list(int), string)
    @return: columnLists
    '''
    selection = request.GET[field]
    if (button == 'removeColumn'):
        availableColumns.append(selection)
        currentColumns.remove(selection)
    elif (button == 'addColumn'):
        currentColumns.append(selection)
        availableColumns.remove(selection)
    elif (button == 'upButton'):
        selectionPos = currentColumns.index(selection)
        if (selectionPos > 0):
            aux = currentColumns[selectionPos - 1]
            currentColumns[selectionPos - 1] = currentColumns[selectionPos]
            currentColumns[selectionPos] = aux
    elif (button == 'downButton'):
        selectionPos = currentColumns.index(selection)
        if (selectionPos < len(currentColumns) - 1):
            aux = currentColumns[selectionPos + 1]
            currentColumns[selectionPos + 1] = currentColumns[selectionPos]
            currentColumns[selectionPos] = aux
    request.session['currentColumns'] = currentColumns
    request.session['availableColumns'] = availableColumns
    columnLists = []
    columnLists.append(currentColumns)
    columnLists.append(availableColumns)
    columnLists.append(selection)
    return columnLists

def _get_exit_policy(rawdesc):
    """
    Gets the exit policy information from the raw descriptor

    @type rawdesc: C{string} or C{buffer}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{list} of C{string}
    @return: all lines in rawdesc that comprise the exit policy.
    """
    policy = []
    rawdesc_array = str(rawdesc).split("\n")
    for line in rawdesc_array:
        if (line.startswith(("accept ", "reject "))):
            policy.append(line)

    return policy


def _is_ip_in_subnet(ip, subnet):
    """
    Return True if the IP is in the subnet, return False otherwise.

    This implementation uses bitwise arithmetic and operators on subnets.

    >>> _is_ip_in_subnet('0.0.0.0', '0.0.0.0/8')
    True
    >>> _is_ip_in_subnet('0.255.255.255', '0.0.0.0/8')
    True
    >>> _is_ip_in_subnet('1.0.0.0', '0.0.0.0/8')
    False

    @type ip: C{string}
    @param ip: The IP address to check for membership in the subnet.
    @type subnet: C{string}
    @param subnet: The subnet that the given IP address may or may not
        be in.
    @rtype: C{boolean}
    @return: True if the IP address is in the subnet, false otherwise.

    @see: U{http://www.webopedia.com/TERM/S/subnet_mask.html}
    @see: U{http://wiki.python.org/moin/BitwiseOperators}
    """
    # If the subnet is a wildcard, the IP will always be in the subnet
    if (subnet == '*'):
        return True

    # If the subnet is the IP, the IP is in the subnet
    if (subnet == ip):
        return True

    # If the IP doesn't match and no bits are provided, the IP is not
    # in the subnet
    if ('/' not in subnet):
        return False

    # Separate the base from the bits and convert the base to an int
    base, bits = subnet.split('/')

    # a.b.c.d becomes a*2^24 + b*2^16 + c*2^8 + d
    a, b, c, d = base.split('.')
    subnet_as_int = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + \
            int(d)

    # Example: if 8 bits are specified, then the mask is calculated by
    # taking a 32-bit integer consisting of 1s and doing a bitwise shift
    # such that only 8 1s are left at the start of the 32-bit integer
    if (int(bits) == 0):
        mask = 0
    else:
        mask = (~0 << (32 - int(bits)))

    # Calculate the lower and upper bounds using the mask.
    # For example, 255.255.128.0/16 should have lower bound 255.255.0.0
    # and upper bound 255.255.255.255. 255.255.128.0/16 is the same as
    # 11111111.11111111.10000000.00000000 with mask
    # 11111111.11111111.00000000.00000000. Then using the bitwise and
    # operator, the lower bound would be
    # 11111111.11111111.00000000.00000000.
    lower_bound = subnet_as_int & mask

    # Similarly, ~mask would be 00000000.00000000.11111111.11111111,
    # so ~mask & 0xFFFFFFFF = ~mask & 11111111.11111111.11111111.11111111,
    # or 00000000.00000000.11111111.11111111. Then
    # 11111111.11111111.10000000.00000000 | (~mask % 0xFFFFFFFF) is
    # 11111111.11111111.11111111.11111111.
    upper_bound = subnet_as_int | (~mask & 0xFFFFFFFF)

    # Convert the given IP to an integer, as before.
    a, b, c, d = ip.split('.')
    ip_as_int = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)

    if (ip_as_int >= lower_bound and ip_as_int <= upper_bound):
        return True
    else:
        return False


def _is_ipaddress(ip):
    """
    Return True if the given supposed IP address could be a valid IP
    address, False otherwise.

    >>> _is_ipaddress('127.0.0.1')
    True
    >>> _is_ipaddress('a.b.c.d')
    False
    >>> _is_ipaddress('127.0.1')
    False
    >>> _is_ipaddress('127.256.0.1')
    False

    @type ip: C{string}
    @param ip: The IP address to test for validity.
    @rtype: C{boolean}
    @return: True if the IP address could be a valid IP address,
        False otherwise.
    """
    # Including period separators, no IP as a string can have more than
    # 15 characters.
    if (len(ip) > 15):
        return False

    # Every IP must be separated into four parts by period separators.
    if (len(ip.split('.')) != 4):
        return False

    # Users can give IP addresses a.b.c.d such that a, b, c, or d
    # cannot be casted to an integer. If a, b, c, or d cannot be casted
    # to an integer, the given IP address is certainly not a
    # valid IP address.
    a, b, c, d = ip.split('.')
    try:
        if (int(a) > 255 or int(a) < 0 or int(b) > 255 or int(b) < 0 or
                int(c) > 255 or int(c) < 0 or int(d) > 255 or
                int(d) < 0):
            return False
    except:
        return False

    return True


def _is_port(port):
    """
    Return True if the given supposed port could be a valid port,
    False otherwise.

    >>> _is_port('80')
    True
    >>> _is_port('80.5')
    False
    >>> _is_port('65536')
    False
    >>> _is_port('foo')
    False

    @type port: C{string}
    @param port: The port to test for validity.
    @rtype: C{boolean}
    @return: True if the given port could be a valid port, False
        otherwise.
    """
    # Ports must be integers and between 0 and 65535, inclusive. If the
    # given port cannot be casted as an int, it cannot be a valid port.
    try:
        if (int(port) > 65535 or int(port) < 0):
            return False
    except ValueError:
        return False

    return True

def _port_match(dest_port, port_line):
    """
    Find if a given port number, as a string, could be defined as "in"
    an expression containing characters such as '*' and '-'.

    >>> _port_match('80', '*')
    True
    >>> _port_match('80', '79-81')
    True
    >>> _port_match('80', '80')
    True
    >>> _port_match('80', '443-9050')
    False

    @type dest_port: C{string}
    @param dest_port: The port to test for membership in port_line
    @type port_line: C{string}
    @param port_line: The port_line that dest_port is to be checked for
        membership in. Can contain * or -.
    @rtype: C{boolean}
    @return: True if dest_port is "in" port_line, False otherwise.
    """
    if (port_line == '*'):
        return True

    if ('-' in port_line):
        lower_str, upper_str = port_line.split('-')
        lower_bound = int(lower_str)
        upper_bound = int(upper_str)
        dest_port_int = int(dest_port)

        if (dest_port_int >= lower_port and
                dest_port_int <= upper_port):
            return True

    if (dest_port == port_line):
        return True

    return False

def _get_if_exists(request, title):
    """
    Process the HttpRequest provided to see if a value, L{title}, is
    provided and retrievable by means of a C{GET}.

    If so, the data itself is returned; if not, an empty string is
    returned.

    @see: U{https://docs.djangoproject.com/en/1.2/ref/request-response/
    #httprequest-object}

    @type request: HttpRequest object
    @param request: The HttpRequest object that contains metadata
        about the request.
    @type title: C{string}
    @param title: The name of the data that may be provided by the
        request.
    @rtype: C{string}
    @return: The data with L{title} referenced in the request, if it
        exists.
    """
    if (title in request.GET and request.GET[title]):
        return request.GET[title].strip()
    else:
        return ""

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
    from django.core.exceptions import ObjectDoesNotExist
    import matplotlib
    from matplotlib.backends.backend_agg import \
            FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

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

    # Return bytes per seconds, not total bandwidth for 15 minutes.
    bps = map(lambda x: x / (15 * 60), tr_list)

    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = str(to_add_date.hour) + ":" + str(to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    ax.plot(dates, bps, color='#66CD00')
    ax.fill_between(dates, 0, bps, color='#D9F3C0')

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize='9')

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')

    ax.set_title("Average Bandwidth Write History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

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
    from matplotlib.dates import DateFormatter

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

    # Return bytes per seconds, not total bandwidth for 15 minutes.
    bps = map(lambda x: x / (15 * 60), tr_list)
    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = str(to_add_date.hour) + ":" + str(to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    ax.plot(dates, bps, color='#68228B')
    ax.fill_between(dates, 0, bps, color='#DAC8E2')

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize='9')

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize('9')

    ax.set_title("Average Bandwidth Read History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

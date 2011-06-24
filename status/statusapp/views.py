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
from django.views.decorators.cache import cache_page
from django.db.models import Max, Sum
from statusapp.models import Statusentry, Descriptor, Bwhist, Geoipdb, \
        TotalBandwidth
from custom.aggregate import CountCase


# To do: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
#@cache_page(60 * 15) # Cache is turned off for development,
                      # but it works.
def index(request):
    """
    Supply a dictionary to the index.html template consisting of a list
    of active relays.
    """
    last_va = Statusentry.objects.aggregate(\
            last=Max('validafter'))['last']

    # This snippet gets relays active in the last 24 hours, but the
    # current TorStatus implementation only gets relays in the last
    # published consensus.
    """
    day_statusentries = Statusentry.objects.filter(\
            validafter__gte=(last_va - datetime.timedelta(days=1)))\
            .order_by('-validafter')
    recent_entries = list(set(day_statusentries))
    """

    # This is closer to what the current TorStatus implementation does.
    # It might not be good design, though.
    statusentries = Statusentry.objects.filter(validafter=last_va)\
            .extra(select={'geoip':
            'geoip_lookup(address)'}).order_by('nickname')

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

    total_bw = TotalBandwidth.objects.all()\
            .order_by('-date')[:1][0].bwobserved

    num_routers = statusentries.count()

    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': statusentries, 'client_address':
            client_address, 'num_routers': num_routers, 'exp_time': 900,
            'counts': counts, 'total_bw': total_bw}
    return render_to_response('index.html', template_values)


def details(request, fingerprint):
    """
    Supply the L{Statusentry} and L{Geoipdb} objects associated with a
    relay with a given fingerprint to the details.html template.
    """
    # [:1] is djangonese for 'LIMIT 1'; [0] gets the object rather than
    # the set.
    statusentry = Statusentry.objects.filter(fingerprint=fingerprint)\
            .extra(select={'geoip': 'geoip_lookup(address)'})\
            .order_by('-validafter')[:1][0]

    # Fails miserably -- gte and lte don't behave properly.
    """
    geoip = Geoipdb.objects.filter(ipstart__gte=statusentry.address,
            ipend__lte=statusentry.address)[:1][0]
    """

    template_values = {'relay': statusentry} #'geoip': geoip}

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


def csv_current_results(request):
    # Does not work yet; waiting for query via Django's ORM.
    """
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test.csv'

    # Table is undefined now, but it should be what is returned by the
    # query.
    writer = csv.writer(response)
    writer.writerow(['variables', 'go', 'here'])
    for row in table:
        writer.writerow(row)

    return response


def networkstatisticgraphs(request):
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

    if not ('currentColumns' in request.session and 'availableColumns' in
            request.session):
        DEFAULT_currentColumns = ["Country Code", "Uptime", "Hostname",
                "ORPort", "DirPort", "IP", "Exit", "Authority", "Fast",
                "Guard", "Named", "Stable", "Running", "Valid",
                "Bandwidth", "V2Dir", "Platform", "Hibernating",
                "BadExit"]
        DEFAULT_availableColumns = ["Fingerprint", "LastDescriptorPublished",
                "Contact", "BadDir", "BadExit"]
        request.session['currentColumns'] = DEFAULT_currentColumns
        request.session['availableColumns'] = DEFAULT_availableColumns
        currentColumns = DEFAULT_currentColumns
        availableColumns = DEFAULT_availableColumns
    else:
        currentColumns = request.session['currentColumns']
        availableColumns = request.session['availableColumns']

    selection = ''
    if ('removeColumn' in request.GET and 'selected_removeColumn' in
            request.GET):
        selection = request.GET['selected_removeColumn']
        availableColumns.append(selection)
        currentColumns.remove(selection)
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns

    if ('addColumn' in request.GET and 'selected_addColumn' in request.GET):
        selection = request.GET['selected_addColumn']
        currentColumns.append(selection)
        availableColumns.remove(selection)
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns

    if ('upButton' in request.GET and 'selected_removeColumn' in request.GET):
        selection = request.GET['selected_removeColumn']
        selectionPos = currentColumns.index(selection)
        if (selectionPos > 0):
            aux = currentColumns[selectionPos - 1]
            currentColumns[selectionPos - 1] = currentColumns[selectionPos]
            currentColumns[selectionPos] = aux
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns

    if ('downButton' in request.GET and 'selected_removeColumn' in
            request.GET):
        selection = request.GET['selected_removeColumn']
        selectionPos = currentColumns.index(selection)
        if (selectionPos < len(currentColumns) - 1):
            aux = currentColumns[selectionPos + 1]
            currentColumns[selectionPos + 1] = currentColumns[selectionPos]
            currentColumns[selectionPos] = aux
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns

    template_values = {'currentColumns': currentColumns, 'availableColumns':
            availableColumns, 'selectedEntry': selection}
    return render_to_response('columnpreferences.html', template_values)


def networkstatisticgraphs(request):
    # For now, this function is just a placeholder.
    """
    """

    variables = "TEMP STRING"
    template_values = {'variables': variables}
    return render_to_response('statisticgraphs.html', template_values)


def unruly_passengers_csv(request):
    # For now, this function is just a placeholder. We're using this to see
    # if we can understand the csv module.
    """
    """
    UNRULY_PASSENGERS = [146, 184, 235, 200, 226, 251, 299, 273, 281, 304,
            203]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test_data.csv'

    # Create the CSV writer using the HttpResponse as the "file."
    writer = csv.writer(response)
    writer.writerow(['Year', 'Unruly Airline Passengers'])
    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
        writer.writerow([year, num])

    return response


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

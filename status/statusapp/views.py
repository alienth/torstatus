from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest, Http404
#from django.views.decorators.cache import cache_page
from django.db import connection
import csv
from django.views.decorators.cache import cache_page
import datetime
import time


# To do: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
#@cache_page(60 * 15) # Cache is turned off for development,
                      # but it works.
def index(request):
    """
    Supply a dictionary to the index.html template consisting of keys
    equivalent to columns in the statusentry and descriptor tables in the
    database. Querying the database is done with raw SQL. This needs 
    to be fixed.
    """
    start = datetime.datetime.now()
    tick = time.clock()

    # Search options should probably not be implemented this way in a 
    # raw SQL query for security reasons:
    #ordering = ""
    #restrictions = ""
    #adv_search = ""
    #if request.GET:

    cursor = connection.cursor()

    cursor.execute('SELECT MAX(validafter) FROM statusentry')

    validafter_range = (cursor.fetchone()[0] - datetime.timedelta(hours=24))

    # Problem: Query takes a LONG time (7.96 sec on wesleyan's server). This
    # should be cached.
    # When a foreign key relationship is defined, this query will be done
    # through Django's ORM.
    # If a statusentry has no descriptor, then the entry is still passed on
    # to the template, but the fields that belong to the descriptor tables
    # are null.
    cursor.execute('SELECT sentry.isbadexit, sentry.isnamed, \
            sentry.fingerprint, sentry.nickname, descriptor.bandwidthobserved, \
            descriptor.uptime, sentry.address, sentry.isfast, sentry.isexit, \
            sentry.isguard, sentry.isstable, sentry.isauthority, \
            descriptor.platform, sentry.orport, sentry.dirport, sentry.isv2dir \
            FROM descriptor RIGHT JOIN (SELECT u.isbadexit, u.isnamed, \
            u.fingerprint, u.nickname, u.address, u.isfast, u.isexit, \
            u.isguard, u.isstable, u.isauthority, u.orport, u.dirport, \
            u.descriptor, u.isv2dir, q.validafter FROM statusentry AS u JOIN \
            (SELECT nickname, MAX(validafter) AS validafter FROM statusentry \
            WHERE validafter > %s GROUP BY nickname) AS q \
            ON u.nickname = q.nickname AND u.validafter = q.validafter WHERE \
            u.validafter > %s) as sentry ON \
            sentry.descriptor = descriptor.descriptor;', \
            [validafter_range, validafter_range])

    relays = cursor.fetchall()
    num_routers = len(relays)
    client_address = request.META['REMOTE_ADDR']
    end = datetime.datetime.now()
    tock = time.clock()
    # proc_time definitely is not accurate -- looks like it doesn't take into
    # account the SQL query work done with cursor
    proc_time = tock - tick
    gen_clock = end - start
    gen_time = str((gen_clock).seconds) + "." + str((gen_clock).microseconds)
    # Note: cache_updated only has meaning if the cache is turned on.
    template_values = {'relay_list': relays, 'client_address': client_address, \
            'cache_updated': end, 'gen_time': gen_time, 'proc_time': proc_time,\
             'num_routers': num_routers, 'exp_time': 900}
    return render_to_response('index.html', template_values)


def customindex(request, fingerprint):
    # This method should probably not exist, and request.GET should be used
    # in statusapp.views.index to make different queries.
    """
    List of variables passed from the html form:

    sortlistings: what to sort by could be (router, fingerprint, country,
    bandwidth, uptime, lastDescriptor, hostname, ip, ORPort, DirPort, platform,
    contact, authority, badDirectory, badExit, exit, fast, guard, hibernating,
    named)

    sortorder: the order to sort by, could be (ascending, descending)

    authority: require flags, could be (yes, no)

    badDirectory: require flags, could be (yes, no)

    BadExit: require flags, could be (yes, no)

    Exit:  require flags, could be (yes, no)

    Fast:  require flags, could be (yes, no)

    Guard: require flags, could be (yes, no)

    Hibernating: require flags, could be (yes, no)

    Named:  require flags, could be (yes, no)

    Stable:  require flags, could be (yes, no)

    Running:  require flags, could be (yes, no)

    Valid:  require flags, could be (yes, no)

    V2Dir:  require flags, could be (yes, no)

    criteria: the criteria for an advanced search could be (fingerprint,
    nickname, country, bandwidth, uptime, published, address, hostname,
    orport, dirport, platform, contact)

    boolLogic: the logic we'd like to use could be 
    (equals, contains, less, greater)

    searchstuff: stuff to searchfor could be (any string)
    """

    #Lots of work to do here. A lot more complicated than initially thought.
    #I need to create the custom index page from all these variables.
    #This means creating tons of different possible tables. I'll get to it
    #eventually.
    #Could even merge with index


    if 'searchstuff' in request.GET:
        if request.GET['searchstuff']:
            message = 'You searched for: %r' % request.GET['searchstuff']
        else:
            message = 'You submitted an empty form.'
    return HttpResponse(message)

def details(request, fingerprint):
    #import geoip
    """
    Supply a dictionary to the details.html template consisting of relevant
    values associated with a given fingerprint. Querying the database is done 
    with raw SQL. This needs to be fixed.
    """

    cursor = connection.cursor()
    cursor.execute('SELECT statusentry.nickname, statusentry.fingerprint, \
            statusentry.address, statusentry.orport, statusentry.dirport, \
            descriptor.platform, descriptor.published, descriptor.uptime, \
            descriptor.bandwidthburst, descriptor.bandwidthavg, \
            descriptor.bandwidthobserved, statusentry.isauthority, \
            statusentry.isbaddirectory, statusentry.isbadexit, \
            statusentry.isexit, statusentry.isfast, statusentry.isguard, \
            statusentry.isnamed, statusentry.isstable, statusentry.isrunning, \
            statusentry.isvalid, statusentry.isv2dir, statusentry.ports, \
            descriptor.rawdesc FROM statusentry JOIN descriptor ON \
            statusentry.descriptor = descriptor.descriptor WHERE \
            statusentry.fingerprint = %s ORDER BY \
            statusentry.validafter DESC LIMIT 1', [fingerprint]) 

    try: 
        nickname, fingerprint, address, orport, dirport, platform, published, \
            uptime, bandwidthburst, bandwidthavg, bandwidthobserved, \
            isauthority, isbaddirectory, isbadexit, isexit, isfast, isguard, \
            isnamed, isstable, isrunning, isvalid, isv2dir, ports, rawdesc \
            = cursor.fetchone()

    except:
        raise Http404
    
    #country = ""
    #country = geoip.country(address)

    template_values = {'nickname': nickname, 'fingerprint': fingerprint, \
            'address': address, 'orport': orport, 'dirport': dirport, \
            'platform': platform, 'published': published, 'uptime': uptime, \
            'bandwidthburst': bandwidthburst, 'bandwidthavg': bandwidthavg, \
            'bandwidthobserved': bandwidthobserved, 'isauthority': isauthority,\
             'isbaddirectory': isbaddirectory, 'isbadexit': isbadexit, \
            'isexit': isexit, 'isfast': isfast, 'isguard': isguard, \
            'isnamed': isnamed, 'isstable': isstable, 'isrunning': isrunning, \
            'isvalid': isvalid, 'isv2dir': isv2dir, 'ports': ports, \
            'rawdesc': rawdesc}#, 'country': country}

    return render_to_response('details.html', template_values)

def exitnodequery(request):
    """
    Determine if an IP address is an active Tor server, and optionally
    see if the server's exit policy would permit it to exit to a given
    destination IP address and port.
    """
    # Given by the client
    source = ""
    dest_ip = ""
    dest_port = ""
    source_valid = False
    dest_ip_valid = False
    dest_port_valid = False

    if ('queryAddress' in request.GET and request.GET['queryAddress']):
        source = request.GET['queryAddress'].strip()
        if (_is_ipaddress(source)):
            source_valid = True
    if ('destinationAddress' in request.GET and \
            request.GET['destinationAddress']):
        dest_ip = request.GET['destinationAddress'].strip()
        if (_is_ipaddress(dest_ip)):
            dest_ip_valid = True
    if ('destinationPort' in request.GET and request.GET['destinationPort']):
        dest_port = request.GET['destinationPort'].strip()
        if (_is_port(dest_port)):
            dest_port_valid = True

    # Some users may assume exiting on port 80. If a destination IP address is
    # given, but no port, assume that the user means port 80.
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
        last_va = Statusentry.objects.aggregate\
                (last=Max('validafter'))['last']
        oldest_tolerable = last_va - datetime.timedelta(days=1)

        recent_entries = Statusentry.objects.filter(address=source, \
                validafter__gte=oldest_tolerable)

        # Group by fingerprints, which are unique. If at least one fingerprint
        # is found, there is a match, so for each fingerprint, get the
        # fingerprint and nickname.
        # TODO: This query is costly; there must be a better way to do it.
        fingerprints = recent_entries.values('fingerprint').annotate(Count('fingerprint'))
        if (fingerprints.count() > 0):
            is_router = True

            # For each entry, gather the nickname and fingerprint. If a 
            # destination IP and port are defined, also find whether or not
            # the entries will allow exiting to the given IP and port.
            for fp_entry in fingerprints:
                # Note that the trailing [:1] is djangonese for "LIMIT 1", 
                # so this query should not be expensive.
                statusentry_set = Statusentry.objects.filter(fingerprint=\
                        fp_entry['fingerprint'], validafter__gte=\
                        (oldest_tolerable)).order_by('-validafter')[:1]
                statusentry = statusentry_set[0]

                nickname = statusentry.nickname
                fingerprint = statusentry.fingerprint
                exit_possible = False

                # If the client also wants to test the relay's exit policy,
                # dest_ip and dest_port cannot be empty strings.
                if (dest_ip_valid and dest_port_valid):
                    descriptor = Descriptor.objects.get(descriptor=\
                            statusentry.descriptor)
                    router_exit_policy = _get_exit_policy(descriptor.rawdesc)

                    # Search the exit policy information for a case in which
                    # the given IP is in a subnet defined in the exit policy
                    # information of a relay.
                    for policy_line in router_exit_policy:
                        condition, network_line = (policy_line.strip())\
                                .split(' ')
                        subnet, port_line = network_line.split(':')

                        # When the IP is in the given subnet, check to ensure
                        # that the given destination port is also in the port
                        # defined in the exit policy information. When a match
                        # is found, see if the condition is "accept" or "reject"
                        if (_is_ip_in_subnet(dest_ip, subnet)):
                            if (_port_match(dest_port, port_line)):
                                if (condition == 'accept'):
                                    exit_possible = True
                                else:
                                    exit_possible = False
                                break

                relays.append((nickname, fingerprint, exit_possible))
          
    template_values = {'is_router': is_router, 'relays': relays, \
            'dest_ip': dest_ip, 'dest_port': dest_port, 'source': source, \
            'source_valid': source_valid, 'dest_ip_valid': dest_ip_valid, \
            'dest_port_valid': dest_port_valid}
    return render_to_response('nodequery.html', template_values)


def csv_current_results(request):
    # Does not work yet; waiting for query via Django's ORM.
    """
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test.csv'

    # Table is undefined now, but it should be what is returned by the query.
    writer = csv.writer(response)
    writer.writerow(['variables', 'go', 'here'])
    for row in table:
        writer.writerow(row)

    return response

def networkstatisticgraphs(request):
    # For now, this function is just a placeholder.

    variables = "TEMP STRING"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def columnpreferences(request):
    '''
    Let the user choose what columns should be displayed on the index page.
    This view makes use of the sessions in order to store two array-list 
    objects (currentColumns and availableColumns) in a "cookie" file so that
    the implementation of the "REMOVE", "ADD", "UP" and "DOWN" options
    from the page could be possible. 
    It orders the two array-lists by using the user input, through a GET 
    single selection HTML form.
    
    @param: request
    @return: renders to the page the currently selected columns, the available 
        columns and the previous selection
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
    
    if not ('currentColumns' in request.session and 'availableColumns' in request.session):
        DEFAULT_currentColumns = ["Country Code", "Uptime", "Hostname", "ORPort", "DirPort", "IP", \
                    "Exit", "Authority", "Fast", "Guard", "Named", "Stable", "Running", "Valid", \
                    "Bandwidth", "V2Dir", "Platform", "Hibernating", "BadExit",]
        DEFAULT_availableColumns = ["Fingerprint", "LastDescriptorPublished", "Contact", "BadDir", "BadExit"]
        request.session['currentColumns'] = DEFAULT_currentColumns
        request.session['availableColumns'] = DEFAULT_availableColumns
        currentColumns = DEFAULT_currentColumns
        availableColumns = DEFAULT_availableColumns
    else:
        currentColumns = request.session['currentColumns']
        availableColumns = request.session['availableColumns']
    
    selection = ''
    if ('removeColumn' in request.GET and 'selected_removeColumn' in request.GET):
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
    
    if ('downButton' in request.GET and 'selected_removeColumn' in request.GET):
        selection = request.GET['selected_removeColumn']
        selectionPos = currentColumns.index(selection)
        if (selectionPos < len(currentColumns) - 1):
            aux = currentColumns[selectionPos + 1]
            currentColumns[selectionPos + 1] = currentColumns[selectionPos]
            currentColumns[selectionPos] = aux
        request.session['currentColumns'] = currentColumns
        request.session['availableColumns'] = availableColumns
        
    
    template_values = {'currentColumns': currentColumns, 'availableColumns': availableColumns, \
                    'selectedEntry': selection}
    return render_to_response('columnpreferences.html', template_values)

def networkstatisticgraphs(request):
    # For now, this function is just a placeholder.
    """
    """

    variables = "TEMP STRING"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)

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

def _get_exit_policy(rawdesc):
    """
    Gets the exit policy information from the raw descriptor

    @rtype      list of strings
    @return     all lines in rawdesc that comprise the exit policy
    """

    policy = []
    rawdesc_array = rawdesc.split("\n")
    for line in rawdesc_array:
        if (line.startswith(("accept ", "reject "))):
            policy.append(line)

    return policy

def _is_ip_in_subnet(ip, subnet):
    """
    Return true if the IP is in the subnet, return false otherwise.

    With credit to the original TorStatus PHP function IsIPInSubnet.

    >>> _is_ip_in_subnet('0.0.0.0', '0.0.0.0/8')
    True
    >>> _is_ip_in_subnet('0.255.255.255', '0.0.0.0/8')
    True
    >>> _is_ip_in_subnet('1.0.0.0', '0.0.0.0/8')
    False

    @type ip: C{string}
    @ivar ip: The IP address to check for membership in the subnet.
    @type subnet: C{string}
    @ivar subnet: The subnet that the given IP address may or may not be in.
    @rtype: C{boolean}
    @return: True if the IP address is in the subnet, false otherwise.
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

    """This implementation uses bitwise arithmetic and operators on subnets.
    @see: U{http://www.webopedia.com/TERM/S/subnet_mask.html}
    @see: U{http://wiki.python.org/moin/BitwiseOperators}"""

    # Separate the base from the bits and convert the base to an int
    base, bits = subnet.split('/')

    # a.b.c.d becomes a*2^24 + b*2^16 + c*2^8 + d
    a, b, c, d = base.split('.')
    subnet_as_int = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)

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
    # operator, the lower bound would be 11111111.11111111.00000000.00000000.
    lower_bound = subnet_as_int & mask

    # Similarly, ~mask would be 00000000.00000000.11111111.11111111, 
    # so ~mask & 0xFFFFFFFF = ~mask & 11111111.11111111.11111111.11111111, or
    # 00000000.00000000.11111111.11111111. Then
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
    Return True if the given supposed IP address could be a valid IP address,
    False otherwise.

    @type ip: C{string}
    @ivar ip: The IP address to test for validity.
    @rtype: C{boolean}
    @return: True if the IP address could be a valid IP address,
        False otherwise.
    """
    # Including period separators, no IP as a string can have more than 15
    # characters.
    if (len(ip) > 15):
        return False

    # Every IP must be separated into four parts by period separators.
    if (len(ip.split('.')) != 4):
        return False

    # Users can give IP addresses a.b.c.d such that a, b, c, or d cannot be
    # casted to an integer. If a, b, c, or d cannot be casted to an integer,
    # the given IP address is certainly not a valid IP address.
    a, b, c, d = ip.split('.')
    try:
        if (int(a) > 255 or int(a) < 0 or int(b) > 255 or int(b) < 0 or int(c) > 255 or int(c) < 0 or int(d) > 255 or int(d) < 0):
            return False
    except:
        return False

    return True

def _is_port(port):
    """
    Return True if the given supposed port could be a valid port, 
    False otherwise.

    @type port: C{string}
    @ivar port: The port to test for validity.
    @rtype: C{boolean}
    @return: True if the given port could be a valid port, False otherwise.
    """
    # Ports must be integers and between 0 and 65535, inclusive. If the given 
    # port cannot be casted as an int, it cannot be a valid port.
    try:
        if (int(port) > 65535 or int(port) < 0):
            return False
    except:
        return False

    return True

def _port_match(dest_port, port_line):
    """
    Find if dest_port is defined as "in" port_line.

    @type dest_port: C{string}
    @ivar dest_port: The port to test for membership in port_line
    @type port_line: C{string}
    @ivar port_line: The port_line that dest_port is to be checked for
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
        if (dest_port_int >= lower_port and dest_port_int <= upper_port):
            return True
    if (dest_port == port_line):
        return True
    return False


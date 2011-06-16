from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest, Http404

#from django.views.decorators.cache import cache_page
from django.db import connection
import csv
import datetime
import time # Processing time, in unix...

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

    if 'searchstuff' in request.GET:
        if request.GET['searchstuff']:
            message = 'You searched for: %r' % request.GET['searchstuff']
        else:
            message = 'You submitted an empty form.'
    return HttpResponse(message)

def details(request, fingerprint):
    """
    Supply a dictionary to the details.html template consisting of relevant
    values associated with a given fingerprint. Querying the database is done 
    with raw SQL. This needs to be fixed.
    """

    from django.db import connection

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
    
    template_values = {'nickname': nickname, 'fingerprint': fingerprint, \
            'address': address, 'orport': orport, 'dirport': dirport, \
            'platform': platform, 'published': published, 'uptime': uptime, \
            'bandwidthburst': bandwidthburst, 'bandwidthavg': bandwidthavg, \
            'bandwidthobserved': bandwidthobserved, 'isauthority': isauthority,\
             'isbaddirectory': isbaddirectory, 'isbadexit': isbadexit, \
            'isexit': isexit, 'isfast': isfast, 'isguard': isguard, \
            'isnamed': isnamed, 'isstable': isstable, 'isrunning': isrunning, \
            'isvalid': isvalid, 'isv2dir': isv2dir, 'ports': ports, \
            'rawdesc': rawdesc}

    return render_to_response('details.html', template_values)

def exitnodequery(request):
    # TODO: given an IP, only one or zero routers are returned, but some
    # routers have the same IP. This method should be fixed to reflect this.
    """
    Determine if an IP address is an active Tor server, and optionally
    see if the server's exit policy would permit it to exit to a given
    destination IP address and port.
    """
    # Given by the client
    source = ""
    dest_ip = ""
    dest_port = ""
    if ('queryAddress' in request.GET and request.GET['queryAddress']):
        source = request.GET['queryAddress']
    if ('destinationAddress' in request.GET and \
            request.GET['destinationAddress']):
        dest_ip = request.GET['destinationAddress']
    if ('destinationPort' in request.GET and request.GET['destinationPort']):
        dest_port = request.GET['destinationPort']

    # To render to response
    is_router = False
    router_fingerprint = ""
    router_nickname = ""
    exit_possible = False

    if source:
        from django.db.models import Max

        last_va = Statusentry.objects.aggregate\
                (last=Max('validafter'))['last']

        recent_relays = Statusentry.objects.filter(address=source, \
                validafter__gte=(last_va - datetime.timedelta(days=1)), \
                ).order_by('-validafter')[:1]

        if (recent_relays.count()):
            is_router = True

            statusentry = recent_relays[0]

            router_nickname = statusentry.nickname
            router_fingerprint = statusentry.fingerprint

            if (dest_ip):
                descriptor = Descriptor.objects.get(descriptor=\
                        statusentry.descriptor)
                router_exit_policy = _get_exit_policy(descriptor.rawdesc)

                for policy_line in router_exit_policy:
                    condition, network_line = (policy_line.strip()).split(' ')
                    subnet, port_line = network_line.split(':')
                    # port = port_line.split(',') # I don't think we need this

                    if (_is_ip_in_subnet(dest_ip, subnet)):
                        if (port_line == '*'):
                            if (condition == 'accept'):
                                exit_possible = True
                                break
                            else:
                                exit_possible = False
                                break

                        elif ('-' in port_line):
                            lower_port, upper_port = port_line.split('-')
                            if (dest_port >= lower_port and dest_port <= \
                                    upper_port):
                                if (condition == 'accept'):
                                    exit_possible = True
                                    break
                                else:
                                    exit_possible = False
                                    break

                        else:
                            if (dest_port == port_line):
                                if (condition == 'accept'):
                                    exit_possible = True
                                    break
                                else:
                                    exit_possible = False
                                    break
                                    
    template_values = {'is_router': is_router, 'router_fingerprint': \
            router_fingerprint, 'router_nickname': router_nickname, \
            'exit_possible': exit_possible, 'dest_ip': dest_ip, 'dest_port': \
            dest_port, 'source': source}
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
    # For now, this function is just a placeholder.

    variables = "TEMP STRING"
    template_values = {'variables': variables,}
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
        if (line.startswith(("accept", "reject"))):
            policy.append(line)

    return policy

def _is_ip_in_subnet(ip, subnet):
    """
    Return true if the IP is in the subnet, return false otherwise.

    With credit to the original TorStatus PHP function IsIPInSubnet.

    >>> _is_ip_in_subnet('0.0.0.0', '0.0.0.0/16')
    True
    >>> _is_ip_in_subnet('0.0.255.255', '0.0.0.0/16')
    True
    >>> _is_ip_in_subnet('0.1.0.0', '0.0.0.0/16')
    False
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

    a, b, c, d = base.split('.')
    subnet_as_int = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)

    if (int(bits) == 0):
        mask = 0
    else:
        mask = (~0 << (32 - int(bits)))

    lower_bound = subnet_as_int & mask

    upper_bound = subnet_as_int | (~mask & 0xFFFFFFFF)

    # Convert the given IP to an integer
    a, b, c, d = ip.split('.')
    ip_as_int = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)

    if (ip_as_int >= lower_bound and ip_as_int <= upper_bound):
        return True
    else:
        return False


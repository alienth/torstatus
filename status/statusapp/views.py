from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest, Http404
from django.db import connection
import csv
from statusapp.models import Statusentry, Descriptor, Bwhist
import datetime
import time
from django.db.models import Max


# To do: get rid of javascript sorting: pass another argument
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
    
    recent_entries = list(set(a))
    
    num_routers = len(recent_entries)
    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': recent_entries, 'client_address': client_address, 'num_routers': num_routers, 'exp_time': 900, \
                    'currentColumns': currentColumns, 'queryOptions': queryOptions}
    return render_to_response('index.html', template_values)

def details(request, descriptor_fingerprint):
    import geoip
    
    #This block gets the specific descriptor and statusentry that the client asked for
    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    day_entries = Statusentry.objects.filter(validafter__gte=(last_va - datetime.timedelta(days=1))).order_by('-validafter')
    entry = list(day_entries.filter(fingerprint = descriptor_fingerprint))[0]
    descriptor = entry.descriptorid
    template_values = {'descriptor': descriptor, 'statusentry': entry}

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
    
    @see: _buttonChoice
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

def graph1(request):
    from statusapp.models import Statusentry, Descriptor, Bwhist
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter


    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    day_entries = Statusentry.objects.filter(validafter__gte=(last_va - datetime.timedelta(days=1))).order_by('-validafter')
    entry = list(day_entries.filter(fingerprint = descriptor_fingerprint))[0]
    descriptor = entry.descriptorid
    bandwidthobject = Bwhist.objects.filter(fingerprint=descriptor_fingerprint)[0]
    """
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.999
    matplotlib.rcParams['figure.subplot.top'] = 0.94
    matplotlib.rcParams['figure.subplot.bottom'] = 0.10
    """
    #
    #
    #
    #    FIRST MAKE GRAPH 1
    #       which is the recent write history graph
    #
    #
    
    x_series = range(0,24)
    y_series = [ bandwidthobject.written[0] for i in x_series]
    pyplot.plot( x_series, y_series, '-')
    pyplot.title( 'Plotting Write history' )
    pyplot.xlabel( 'Hour' )
    pyplot.ylabel( 'Write Speed' )
    pyplot
    
    """
    fig1 = Figure(facecolor='white', edgecolor='black', figsize=(20,5), frameon=False)
    ax = fig.add_subplot(111)

    x = matplotlib.numpy.arange(24)
    """

    p = get_object_or_404(Poll, pk=poll_id)
    #fig = Figure()
    fig = Figure(facecolor='white', edgecolor='black', figsize=(20, 5), frameon=False)
    ax = fig.add_subplot(111)
	
    x = matplotlib.numpy.arange(p.choice_set.count())
    choices = p.choice_set.all()
    choice_votes = [choice.votes for choice in choices][:90]
    choice_names = [choice.choice for choice in choices][:90]
	
    #choice_totalNumber = p.choice_set.count()
    choice_totalNumber = len(choice_names)
    choice_index = matplotlib.numpy.arange(choice_totalNumber)
    
    cols = ['lightblue']
    #cols = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'indigo'] * 10

    cols = cols[0:len(choice_index)]
    bar_width = 0.3
    ax.bar(choice_index, choice_votes, color=cols, width=bar_width)
    ax.set_xticks(choice_index + (bar_width/2.0))
    ax.set_xticklabels(choice_names, fontstyle='italic', fontsize='10', fontweight='light', rotation='vertical', fontname='Others')
    ax.set_xlabel("Choices")
    ax.set_ylabel("Votes")
    chart_title = "Results for poll: %s" % p.question
    ax.set_title(chart_title)
    ax.grid(color='r', linestyle='-', linewidth=.1)
    for index in choice_index:
        ax.text(index, choice_votes[index], str(choice_votes[index]), fontsize='10')
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

def graph2(request):
    #
    #
    #       SECOND MAKE SECOND GRAPH
    #           which is the recent read history
    #
    #

    from statusapp.models import Statusentry, Descriptor, Bwhist
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter


    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    day_entries = Statusentry.objects.filter(validafter__gte=(last_va - datetime.timedelta(days=1))).order_by('-validafter')
    entry = list(day_entries.filter(fingerprint = descriptor_fingerprint))[0]
    descriptor = entry.descriptorid
    bandwidthobject = Bwhist.objects.filter(fingerprint=descriptor_fingerprint)[0]
    """
    matplotlib.rcParams['figure.subplot.left'] = 0.04
    matplotlib.rcParams['figure.subplot.right'] = 0.999
    matplotlib.rcParams['figure.subplot.top'] = 0.94
    matplotlib.rcParams['figure.subplot.bottom'] = 0.10
    """
    
    x_series = range(0,24)
    y_series = [ bandwidthobject.written[0] for i in x_series]
    pyplot.plot( x_series, y_series, '-')
    pyplot.title( 'Plotting Write history' )
    pyplot.xlabel( 'Hour' )
    pyplot.ylabel( 'Write Speed' )
    pyplot
    

    """
    fig1 = Figure(facecolor='white', edgecolor='black', figsize=(20,5), frameon=False)
    ax = fig.add_subplot(111)

    x = matplotlib.numpy.arange(24)
    """

    p = get_object_or_404(Poll, pk=poll_id)
    #fig = Figure()
    fig = Figure(facecolor='white', edgecolor='black', figsize=(20, 5), frameon=False)
    ax = fig.add_subplot(111)
    
    x = matplotlib.numpy.arange(p.choice_set.count())
    choices = p.choice_set.all()
    choice_votes = [choice.votes for choice in choices][:90]
    choice_names = [choice.choice for choice in choices][:90]
    
    #choice_totalNumber = p.choice_set.count()
    choice_totalNumber = len(choice_names)
    choice_index = matplotlib.numpy.arange(choice_totalNumber)
    
    cols = ['lightblue']
    #cols = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'indigo'] * 10

    cols = cols[0:len(choice_index)]
    bar_width = 0.3
    ax.bar(choice_index, choice_votes, color=cols, width=bar_width)
    ax.set_xticks(choice_index + (bar_width/2.0))
    ax.set_xticklabels(choice_names, fontstyle='italic', fontsize='10', fontweight='light', rotation='vertical', fontname='Others')
    ax.set_xlabel("Choices")
    ax.set_ylabel("Votes")
    chart_title = "Results for poll: %s" % p.question
    ax.set_title(chart_title)
    ax.grid(color='r', linestyle='-', linewidth=.1)
    for index in choice_index:
        ax.text(index, choice_votes[index], str(choice_votes[index]), fontsize='10')
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

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

# Django-specific import statements -----------------------------------
from django.http import HttpRequest 


def filter_statusentries(statusentries, query_options):
    """
    Helper function that gets a QuerySet of status entries and a
    dictionary of search query options and filteres the QuerySet
    based on this dictionary.
    
    @see: index
    @rtype: QuerySet
    @return: statusentries
    """
    
    # ADD ishibernating AFTER WE KNOW HOW TO CHECK THAT
    options = ['isauthority', 'isbaddirectory', 'isbadexit', \
               'isexit', 'isfast', 'isguard', 'isnamed', \
               'isstable', 'isrunning', 'isvalid', 'isv2dir']
    # options is needed because query_options has some other things that we 
    #      do not need in this case (the other search query key-values).
    valid_options = filter(lambda k: query_options[k] != '' \
                            and k in options, query_options)
    filterby = {}
    for opt in valid_options: 
        filterby[opt] = 1 if query_options[opt] == 'yes' else 0
 
    if 'searchValue' in query_options and \
                query_options['searchValue'] != '':
        value = query_options['searchValue']
        criteria = query_options['criteria']
        logic = query_options['boolLogic']
            
        options = ['nickname', 'fingerprint', 'geoip',
                   'published','hostname', 'address', 
                   'orport', 'dirport']            
        descriptorlist_options = ['platform', 'uptime', 'bandwidthobserved'] 

        # Special case for the value if searching for 
        #       Uptime or Bandwidth and the criteria is 
        #       not Contains
        if (criteria == 'uptime' or criteria == 'bandwidthobserved') and \
                logic != 'contains': 
            value = int(value) * (86400 if criteria == 'uptime' else 1024)
           

        key = ('descriptorid__' + criteria) if criteria in \
                descriptorlist_options else criteria
      
        if logic == 'contains':
            key = key + '__contains'
        elif logic == 'less':
            key = key + '__lt'
        elif logic == 'greater':
            key = key + '__gt'
        
        if (criteria == 'uptime' or criteria == 'bandwidthobserved') and \
                logic == 'equals':
            lower_value = value
            upper_value = lower_value + (86400 if criteria == 'uptime' else 1024)
            filterby[key + '__gt'] = lower_value
            filterby[key + '__lt'] = upper_value
        else:
            filterby[key] = value
        
    statusentries = statusentries.filter(**filterby)
    
    options = ['nickname', 'fingerprint', 'geoip', 'bandwidthobserved',
               'uptime', 'published','hostname', 'address', 'orport', 
               'dirport', 'platform', 'isauthority', 
               'isbaddirectory', 'isbadexit', 'isexit',
               'isfast', 'isguard', 'ishibernating', 
               'isnamed', 'isstable', 'isrunning', 
               'isvalid', 'isv2dir']

    descriptorlist_options = ['platform', 'uptime', 'contact', 'bandwidthobserved']
    if 'sortListings' in query_options: 
        selected_option = query_options['sortListings']
    else:
        selected_option = ''
    if selected_option in options:
        if selected_option in descriptorlist_options:
            selected_option = 'descriptorid__' + selected_option
        if query_options['sortOrder'] == 'ascending':
            statusentries = statusentries.order_by(selected_option)
        elif query_options['sortOrder'] == 'descending':
            statusentries = statusentries.order_by('-' + selected_option)
    return statusentries

def button_choice(request, button, field, current_columns,
        available_columns):
    """
    Helper function that manages the changes in the L{columnpreferences}
    arrays/lists.

    @rtype: list(list(int), list(int), string)
    @return: column_lists
    """
    selection = request.GET[field]
    if (button == 'removeColumn'):
        available_columns.append(selection)
        current_columns.remove(selection)
    elif (button == 'addColumn'):
        current_columns.append(selection)
        available_columns.remove(selection)
    elif (button == 'upButton'):
        selection_pos = current_columns.index(selection)
        if (selection_pos > 0):
            aux = current_columns[selection_pos - 1]
            current_columns[selection_pos - 1] = \
                           current_columns[selection_pos]
            current_columns[selection_pos] = aux
    elif (button == 'downButton'):
        selection_pos = current_columns.index(selection)
        if (selection_pos < len(current_columns) - 1):
            aux = current_columns[selection_pos + 1]
            current_columns[selection_pos + 1] = \
                           current_columns[selection_pos]
            current_columns[selection_pos] = aux
    request.session['currentColumns'] = current_columns
    request.session['availableColumns'] = available_columns
    column_lists = []
    column_lists.append(current_columns)
    column_lists.append(available_columns)
    column_lists.append(selection)
    return column_lists


def get_exit_policy(rawdesc):
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


def is_ip_in_subnet(ip, subnet):
    """
    Return True if the IP is in the subnet, return False otherwise.

    This implementation uses bitwise arithmetic and operators on
    subnets.

    >>> is_ip_in_subnet('0.0.0.0', '0.0.0.0/8')
    True
    >>> is_ip_in_subnet('0.255.255.255', '0.0.0.0/8')
    True
    >>> is_ip_in_subnet('1.0.0.0', '0.0.0.0/8')
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


def is_ipaddress(ip):
    """
    Return True if the given supposed IP address could be a valid IP
    address, False otherwise.

    >>> is_ipaddress('127.0.0.1')
    True
    >>> is_ipaddress('a.b.c.d')
    False
    >>> is_ipaddress('127.0.1')
    False
    >>> is_ipaddress('127.256.0.1')
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
            int(c) > 255 or int(c) < 0 or int(d) > 255 or int(d) < 0):
            return False
    except:
        return False

    return True


def is_port(port):
    """
    Return True if the given supposed port could be a valid port,
    False otherwise.

    >>> is_port('80')
    True
    >>> is_port('80.5')
    False
    >>> is_port('65536')
    False
    >>> is_port('foo')
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


def port_match(dest_port, port_line):
    """
    Find if a given port number, as a string, could be defined as "in"
    an expression containing characters such as '*' and '-'.

    >>> port_match('80', '*')
    True
    >>> port_match('80', '79-81')
    True
    >>> port_match('80', '80')
    True
    >>> port_match('80', '443-9050')
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


def get_if_exists(request, title):
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


def contact(rawdesc):
    """
    Get the contact information of a relay from its raw descriptor.

    It is possible that a relay will not publish any contact information.
    In this case, "No contact information given" is returned.

    @type rawdesc: C{string} or C{buffer}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The contact information of the relay.
    """

    for line in str(rawdesc).split("\n"):
        if (line.startswith("contact")):
            return line[8:]
    return "No contact information given"

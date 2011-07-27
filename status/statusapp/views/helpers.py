"""
Helper functions for views.csvs, views.graphs, and views.pages.
"""
# General import statements -------------------------------------------
import datetime

# Django-specific import statements -----------------------------------
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse

# Matplotlib-specific import statements -------------------------------
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# TorStatus-specific import statements --------------------------------
from statusapp.models import Bwhist, Descriptor

# INIT Variables ------------------------------------------------------
COLUMN_VALUE_NAME = {'Country Code': 'country',
                     'Router Name': 'nickname',
                     'Bandwidth': 'bandwidthkbps',
                     'Uptime': 'uptime',
                     'IP': 'address',
                     'Hostname': 'hostname',
                     'Icons': 'icons',
                     'ORPort': 'orport',
                     'DirPort': 'dirport',
                     'BadExit': 'isbadexit',
                     'Named': 'isnamed',
                     'Exit': 'isexit',
                     'Authority': 'isauthority',
                     'Fast': 'isfast',
                     'Guard': 'isguard',
                     'Stable': 'isstable',
                     'Valid': 'isvalid',
                     'Directory': 'isv2dir',
                     'Platform': 'platform',
                     'Fingerprint': 'fingerprint',
                     'Last Descriptor Published': 'published',
                     'Contact': 'contact',
                     'BadDir': 'isbaddirectory',
                    }

NOT_COLUMNS = set(('Running', 'Hostname', 'Named', 'Valid'))

ICONS = ['Fast', 'Exit', 'Valid', 'V2Dir', 'Guard', 'Stable', 
         'Authority', 'Platform']

FLAGS = set(('isauthority',
              'isbaddirectory',
              'isbadexit',
              'isexit',
              'isfast',
              'isguard',
              'ishibernating',
              'isnamed',
              'isstable',
              'isvalid',
              'isv2dir'))
SEARCHES = set(('fingerprint',
                 'nickname',
                 'country',
                 'bandwidthkbps',
                 'uptimedays',
                 'published',
                 'address',
                 'orport',
                 'dirport',
                 'platform'))
CRITERIA = set(('exact',
                 'iexact',
                 'contains',
                 'icontains',
                 'lt',
                 'gt',
                 'startswith',
                 'istartswith'))

SORT_OPTIONS = set((
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


def button_choice(request, button, field, current_columns,
        available_columns):
    """
    Helper function that manages the changes in the L{columnpreferences}
    arrays/lists.

    @type button: C{string}
    @param button: A string that indicates which button was clicked.
    @type field: C{string}
    @param field: A string that indicates from which preferences column
        was the corresponding value selected
        (ADD column, REMOVE column).
    @type current_columns: C{list}
    @param current_columns: A list of the columns that will be
        displayed on this session.
    @type available_columns: C{list}
    @param available_columns: A list of the columns that can be added
        to the current ones.
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
    except ValueError:
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
    # If port_line is a wildcard character, dest_port is always 'in'
    # port_line
    if (port_line == '*'):
        return True

    # If port_line contains a dash, a range is given, so get upper
    # and lower bounds.
    if ('-' in port_line):
        lower_str, upper_str = port_line.split('-')
        lower_bound = int(lower_str)
        upper_bound = int(upper_str)
        dest_port_int = int(dest_port)

        if (dest_port_int >= lower_bound and
            dest_port_int <= upper_bound):
            return True

    # If the dest_port is exactly the port_line, then dest_port is
    # 'in' port_line
    if (dest_port == port_line):
        return True

    # port_line must either be a port number, a range of port numbers,
    # or a wildcard character, so if no matches are found, return False
    return False


def sorting_link(sort_order, column_name):
    """
    Returns the proper URL after checking how the sorting is currently
    set up.

    @type sort_order: C{string}
    @param sort_order: A string - the type of order
        (ascending/descending).
    @type column_name: C{string}
    @param column_name: A string - the name of the column that is
                    currently ordering by.
    @rtype: C{string}
    @return The proper link for sorting the tables.
    """
    if sort_order == "ascending":
        return "/index/" + column_name + "_descending"
    return "/index/" + column_name + "_ascending"


def get_filter_params(request):
    """
    Get the filter preferences provided by the user via the
    HttpRequest.

    @type request: HttpRequest
    @param request: The HttpRequest provided by the client
    @rtype: C{dict} of C{string} to C{string}
    @return: A dictionary mapping query parameters to user-supplied
        input.
    """
    filters = {}

    if 'filters' not in request.session:
        # Add filters for flags only if the parameter is a 0 or a 1
        for flag in FLAGS:
            filt = request.GET.get(flag, '')

            if filt == '1':
                filters[flag] = 1

            elif filt == '0':
                filters[flag] = 0

        # Add search filters only if a search term is provided. Search
        # terms are denoted by s_[term]. Similarly, criteria is denoted
        # by c_[term].
        for search in SEARCHES:
            search_param = ''.join(('s_', search))
            searchinput = request.GET.get(search_param, '')

            if searchinput:
                criteria_param = ''.join(('c_', search))
                criteriainput = request.GET.get(criteria_param , '')

                # Format the key for django's filter
                if criteriainput in CRITERIA:
                    key = '__'.join((search, criteriainput))
                    filters[key] = searchinput

        request.session['filters'] = filters

    filters = request.session['filters']
    return filters

def get_order(request):
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
    # Get the order bit -- that is, '-' or the empty string.
    # If neither descending or ascending is given, choose ascending.
    order = request.GET.get('sortOrder', 'ascending')
    orderbit = ''
    if order == 'descending':
        orderbit = '-'

    # Get the order parameter.
    # If the given value is not a valid parameter, choose nickname.
    param = request.GET.get('sortListing', 'nickname')
    if param not in SORT_OPTIONS:
        param = 'nickname'

    return ''.join((orderbit, param))


def gen_list_dict(active_relays):
    """
    Method that generates a list of dictionaries, where each dictionary
    contains the fields of a relay.
    
    @type active_relays: C{QuerySet}
    @param active_relays: A set of all the relays that are going to be 
                        displayed.
    @rtype: C{list}
    @return: A list of dictionaries - each dictionary contains the fields
            of a relay.
    """
    list_dict = []
    if active_relays:
        for relay in active_relays:
            relay_dict = {'isbadexit': 1 if relay.isbadexit else 0,
                          'country': relay.country,
                          'longitude': relay.longitude,
                          'latitude': relay.latitude,
                          'nickname': relay.nickname,
                          'bandwidthkbps': str(relay.bandwidthkbps) + " Kb/s",
                          'uptime': str(relay.uptimedays) + " d",
                          'address': relay.address,
                          #'hostname': relay.hostname,
                          'hibernating': 1 if relay.ishibernating else 0, 
                          'orport': relay.orport,
                          'dirport': relay.dirport,
                          'isbadexit': 1 if relay.isbadexit else 0,
                          'isnamed': 1 if relay.isnamed else 0,
                          'isexit': 1 if relay.isexit else 0,
                          'isauthority': 1 if relay.isauthority else 0,
                          'isfast': 1 if relay.isfast else 0,
                          'isguard': 1 if relay.isguard else 0,
                          'isstable': 1 if relay.isstable else 0,
                          'isv2dir': 1 if relay.isv2dir else 0,
                          'platform': relay.platform,
                          'fingerprint': relay.fingerprint,
                          'published': relay.published,
                          'contact': relay.contact,
                          'isbaddirectory': 1 if relay.isbaddirectory else 0,
                         }
            list_dict.append(relay_dict)
    return list_dict


def gen_relay_dict(relay):
    """
    Method that generates a dictionary of all the fields of a relay.
    
    @type relay: C{ActiveRelay}
    @param relay: The relay for which the fields are going to be generated.
    @rtype: C{dict}
    @return: Dictioanary of the Field Name(key): Field Value(value) for the
            specific relay.
    """
    relay_dict = {'Router Name': relay.nickname,
                  'Fingerprint': relay.fingerprint,
                  'Active Relay': 'Yes' if relay.active else 'No',
                  'Last Consensus Present (GMT)': relay.validafter,
                  'IP Address': relay.address,
                  'Hostname': relay.hostname,
                  'Onion Router Port': relay.orport,
                  'Directory Server Port': relay.dirport,
                  'Country': relay.country,
                  'Latitude, Longitude': str(relay.latitude) + ', ' + \
                            str(relay.longitude),
                  'Platform / Version': relay.platform,
                  'Last Descriptor Published (GMT)': relay.published,
                  'Published Uptime': relay.uptime,
                  'Bandwidth (Burst/Avg/Observed - In Bps)': \
                            str(relay.bandwidthburst) + ' / ' + \
                            str(relay.bandwidthavg) + ' / ' + \
                            str(relay.bandwidthobserved),
                  'Contact': relay.contact,
                  'Family': relay.family,
                  'Authority': 1 if relay.isauthority else 0,
                  'Bad Directory': 1 if relay.isbaddirectory else 0,
                  'Bad Exit': 1 if relay.isbadexit else 0,
                  'Exit': 1 if relay.isexit else 0,
                  'Guard': 1 if relay.isguard else 0,
                  'Fast': 1 if relay.isfast else 0,
                  'Named': relay.isnamed,
                  'Stable': relay.isstable,
                  'Running': relay.isrunning,
                  'Valid': relay.isvalid,
                  'V2Dir': relay.isv2dir, 
                  'HS Directory': relay.ishsdir,                 
                 }
    if relay.hasdescriptor:
        relay_dict['Hibernating'] = 1 if relay.ishibernating else 0
        relay_dict['Adjusted Uptime'] = relay.adjuptime
    else:
        relay_dict['Hibernating'] = 0
        relay_dict['Adjusted Uptime'] = None
    return relay_dict


def gen_options_list(relay):
    """
    Method that generates a list of the fields that will be displayed 
    on the details page of a specific relay.
    
    @type relay: C{ActiveRelay}
    @param relay: The relay for which the list of fields will be generated
    @rtype: C{list}
    @return: List of the fields that will be displayed at the 
        bottom of the details page.
    """
    options_list = ['Router Name', 'Fingerprint', 'Active Relay',]
    if relay.active:
        if relay.hasdescriptor:
            options_list.append('Adjusted Uptime')
    else:
        options_list.append('Last Consensus Present (GMT)')  
    options_list.extend(['IP Address', 'Hostname', 'Onion Router Port',
                    'Directory Server Port', 'Country',
                    'Latitude, Longitude',])                
    if relay.hasdescriptor:
        descriptor_options_list = ['Platform / Version', 
                    'Last Descriptor Published (GMT)', 'Published Uptime',
                    'Bandwidth (Burst/Avg/Observed - In Bps)', 'Contact',
                    'Family',]
        options_list.extend(descriptor_options_list)
    return options_list

def gen_flags_list(relay):
    """
    Method that generates a list of the fields(flags) that will be displayed 
    on the details page of a specific relay.
    
    @type relay: C{ActiveRelay}
    @param relay: The relay for which the list of fields will be generated
    @rtype: C{list}
    @return: List of the fields(flags) that will be displayed at the 
        bottom of the details page.
    """
    flags_list = ['Authority', 'Bad Directory', 'Bad Exit', 'Exit', 'Fast', 
                'Guard', 'HS Directory',]
    if relay.hasdescriptor:
        flags_list.append('Hibernating')
    flags_list.extend(['Named', 'Stable', 'Running', 'Valid', 'V2Dir'])
    return flags_list

"""
Helper functions for views.csvs, views.graphs, and views.pages.
"""
# General import statements -------------------------------------------
import datetime

# Django-specific import statements -----------------------------------
from django.http import HttpRequest
from django.http import HttpResponse

# Matplotlib-specific import statements -------------------------------
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# TorStatus-specific import statements --------------------------------
from statusapp.models import Bwhist

# INIT Variables ------------------------------------------------------
COLUMN_VALUE_NAME = {'Country Code': 'geoip', 
                     'Router Name': 'nickname', 
                     'Bandwidth': 'bandwidthobserved', 
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
                     'Running': 'isrunning',
                     'Valid': 'isvalid',
                     'V2Dir': 'isv2dir',
                     'Platform': 'platform',
                     'Fingerprint': 'fingerprint',
                     'LastDescriptorPublished': 'published',
                     'Contact': 'contact',
                     'BadDir': 'isbaddirectory',
                    }
    
NOT_COLUMNS = ['Running', 'Hostname', 'Named', 'Valid',]
    
ICONS = ['Fast', 'Exit', 'V2Dir', 'Guard', 'Stable', 'Authority', 
         'Platform',]


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
               'uptime', 'published', 'hostname', 'address', 'orport', 
               'dirport', 'platform', 'isauthority', 
               'isbaddirectory', 'isbadexit', 'isexit',
               'isfast', 'isguard', 'isnamed', 'isstable', 'isrunning', 
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


def sorting_link(sort_order, column_name):
    """
    Returns the proper URL after checking how the sorting is currently set up.
    
    @rtype: C{string}
    @return The proper link for sorting the tables.
    """
    
    if sort_order == "ascending":
        return "/" + column_name + "_descending"
    return "/" + column_name + "_ascending"
    
 
def kilobytes_ps(bytes_ps):
    """
    Convert a bandwidth value in bytes to a bandwidth value in kilobytes

    @type bytes_ps: C{int}, C{float}, C{long}, or C{string}
    @param bytes_ps: The bandwidth value, in bps.
    @rtype: C{int}
    @return: The bandwidth value in kbps.
    """
    # As statusapp.views.details is written now, this value can
    # be None or an empty string sometimes.
    if (bytes_ps == '' or bytes_ps is None):
        return 0
    else:
        return int(bytes_ps) / 1024
        

def days(seconds):
    """
    Convert an duration in seconds to an uptime in days, rounding down.

    @type seconds: C{int}, C{float}, C{long}, or C{string}
    @param seconds: The duration in seconds.
    @rtype: C{int}
    @return: The duration in days.
    """
    # As statusapp.views.details is written now, this value can
    # be None or an empty string sometimes.
    if (seconds == '' or seconds is None):
        return 0
    else:
        return int(seconds) / 86400
        

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
            contact_raw = line[8:]
            return contact_raw.decode('raw_unicode_escape')
    return "No contact information given"
    

def country(location):
    """
    Get the country associated with a tuple as a string consisting of
    a country, a latitude, and a longitude.

    >>> getcountry('(US,-43.0156,68.2351)')
    'US'

    @type location: C{string}
    @param location: A tuple consisting of a country, latitude, and
        longitude as a string.
    @rtype: C{string}
    @return: The country code in the tuple as a string.
    """
    return location[1:3].lower()


def latitude(geoip):
    """
    Get the latitude from a GeoIP string.

    @type geoip: C{string} or C{buffer}
    @param geoip: A string formatted as a tuple with entries country
        code, latitude, and longitude.
    @rtype: C{string}
    @return: The latitude associated with C{geoip}.
    """
    return str(geoip).split(',')[1]


def longitude(geoip):
    """
    Get the longitude from a GeoIP string.

    @type geoip: C{string} or C{buffer}
    @param geoip: A string formatted as a tuple with entries country
        code, latitude, and longitude.
    @rtype: C{string}
    @return: The longitude associated with C{geoip}.
    """
    return str(geoip).strip('()').split(',')[2]


def get_platform(platform):
    """
    Method that searches in the platform string for the corresponding 
    platform name.
    
    @rtype: C{string}
    @return: The platform name of the relay.
    """
    # Dictionary of {NameInPlatform: NameOfTheIcon}
    supported_platforms = {'Linux': 'Linux',
                           'XP': 'WindowsXP',
                           'Windows Server': 'WindowsServer',
                           'Windows': 'WindowsOther',
                           'Darwin': 'Darwin',
                           'FreeBSD': 'FreeBSD',
                           'NetBSD': 'NetBSD',
                           'OpenBSD': 'OpenBSD',
                           'SunOS': 'SunOS',
                           'IRIX': 'IRIX', 
                           'Cygwin': 'Cygwin',
                           'Dragon': 'Dragon',
                          }
    for name in supported_platforms:
        if name in platform:
            return supported_platforms[name]
    return None


def generate_table_headers(current_columns, order_column_name, sort_order):
    """ 
    Generates a dictionary of {header_name: html_string_code}. 
    
    @rtype: C{dict}, C{list}
    @return: Dictionary that contains the header name and the HTML code.
        List of the current columns that will be displayed.
    """
    
    # NOTE: The html_current_columns list is needed to preserve the order
    #   of the displayed columns. It is used in the template to iterate
    #   through the current columns in the right order that they should be
    #   displayed.
    
    html_table_headers = {}
    html_current_columns = []
    for column in current_columns:
        database_name = COLUMN_VALUE_NAME[column]
        display_name = "&nbsp;&nbsp;" if column == "Country Code" else column
        sort_arrow = ''
        if order_column_name == database_name:
            if sort_order == 'ascending':
                sort_arrow = "&uarr;"
            elif sort_order == 'descending':
                sort_arrow = "&darr;"
        html_class = "relayHeader hoverable" if database_name != "icons" \
                                                else "relayHeader"    
                                           
        if column not in ICONS and column not in NOT_COLUMNS:
            if column == "Icons":
                if filter(lambda c: c in current_columns, ICONS):
                    html_table_headers[column] = "<th class='" + html_class + "' id='" \
                                        + database_name + "'>" + display_name + "</th>"
                    html_current_columns.append(column)
            else:
                html_table_headers[column] = "<th class='" + html_class + "' id='" \
                                    + database_name + "'><a class='sortLink' \
                                    href='" + sorting_link(sort_order, database_name) \
                                    + "'>" + display_name + " " + sort_arrow + "</a></th>"
                html_current_columns.append(column)
    return html_table_headers, html_current_columns 
    
    
def generate_table_rows(statusentries, current_columns, html_current_columns):
    """
    Generates a list of HTML strings. Each string represents a row in the 
    main template table.
    
    @rtype: C{list}
    @return: List of HTML strings.
    """
    
    html_table_rows = []
    
    for relay in statusentries:
    
        #TODO: CLEAN THE CODE - QUERY ONLY ON THE NECESSARY COLUMNS 
        #               AND THROW IN DICTIONARY AFTERWARDS!!!
        
        # Declarations in order to avoid multiple queries. 
        r_isbadexit = relay.isbadexit      
        field_isbadexit = "<img src='static/img/bg_" + ("yes" if r_isbadexit else "no") + \
                        ".png' width='12' height='12' alt='" + ("Bad Exit' title='Bad Exit'" \
                        if r_isbadexit else "Not a Bad Exit' title='Not a Bad Exit'") + ">"  
        field_geoip = relay.geoip
        field_isnamed = relay.isnamed
        field_fingerprint = relay.fingerprint
        field_nickname = relay.nickname
        field_bandwidthobserved = str(kilobytes_ps(relay.descriptorid.bandwidthobserved)) + \
                                  " KB/s"
        field_uptime = str(days(relay.descriptorid.uptime)) + " d"
        r_address = relay.address
        field_address = "[<a href='details/" + r_address + "/whois'>" + \
                        r_address + "</a>]"
        field_published = str(relay.published)
        field_contact = contact(relay.descriptorid.rawdesc)
        r_isbaddir = relay.isbaddirectory
        field_isbaddirectory = "<img src='static/img/bg_" + ("yes" if r_isbaddir else "no") + \
                        ".png' width='12' height='12' alt='" + ("Bad Directory' title='Bad Directory'" \
                        if r_isbaddir else "Not a Bad Directory' title='Not a Bad Directory'") + ">"                   
        field_isfast = "<img src='static/img/status/Fast.png' alt='Fast Server' title='Fast Server'>" \
                        if relay.isfast else ""
        field_isv2dir = "<img src='static/img/status/Dir.png' alt='Directory Server' title='Directory Server'>" \
                        if relay.isv2dir else ""
        field_isexit = "<img src='static/img/status/Exit.png' alt='Exit Server' title='Exit Server'>" \
                        if relay.isexit else ""
        field_isguard = "<img src='static/img/status/Guard.png' alt='Guard Server' title='Guard Server'>" \
                        if relay.isguard else ""
        field_isstable = "<img src='static/img/status/Stable.png' alt='Stable Server' title='Stable Server'>" \
                        if relay.isstable else ""
        field_isauthority = "<img src='static/img/status/Authority.png' alt='Authority Server' title='Authority Server'>" \
                        if relay.isauthority else ""
        r_platform = relay.descriptorid.platform
        r_os_platform = get_platform(r_platform)
        field_platform = "<img src='static/img/os-icons/" + r_os_platform + ".png' alt='" + r_os_platform + \
                         "' title='" + r_platform + "'>" if r_os_platform else ""
        field_orport = str(relay.orport)
        r_dirport = str(relay.dirport)
        field_dirport = r_dirport if r_dirport else "None"
        
        
        RELAY_FIELDS = {'isbadexit': field_isbadexit,
                        'geoip': field_geoip,
                        'isnamed': field_isnamed,
                        'fingerprint': field_fingerprint,
                        'nickname': field_nickname,
                        'bandwidthobserved': field_bandwidthobserved,
                        'uptime': field_uptime,
                        'address': field_address,
                        'published': field_published,
                        'contact': field_contact,
                        'isbaddirectory': field_isbaddirectory,
                        'isfast': field_isfast,
                        'isv2dir': field_isv2dir,
                        'isexit': field_isexit, 
                        'isguard': field_isguard,
                        'isstable': field_isstable,
                        'isauthority': field_isauthority,
                        'platform': field_platform,
                        'orport': field_orport,
                        'dirport': field_dirport,
                       }                  
                        
        html_row_code = ''
        
        if 'isbadexit' in RELAY_FIELDS:
            html_row_code = "<tr " + ("class='relayBadExit'" if r_isbadexit \
                            else "class='relay'") + ">"
        else:
            html_row_code = "<tr class='relay'>"
            
        for column in html_current_columns:
            value_name = COLUMN_VALUE_NAME[column]
            
            # Special Case: Country Code
            if column == 'Country Code':
                c_country = country(RELAY_FIELDS[value_name])
                c_latitude = latitude(RELAY_FIELDS[value_name])
                c_longitude = longitude(RELAY_FIELDS[value_name])               
                html_row_code = html_row_code + "<td id='col_relayName'><a href=\
                                'http://www.openstreetmap.org/?mlon=" + c_longitude + \
                                "&mlat=" + c_latitude + "&zoom=6'> \
                                <img src='static/img/flags/" + c_country + \
                                ".gif' alt='" + c_country + "' title='" + \
                                c_country + ":" + c_latitude + ", " + \
                                c_longitude + "' border=0></a></td>"
            # Special Case: Router Name and Named
            elif column == 'Router Name':
                if 'Named' in current_columns:
                    html_router_name = "<a href='/details/" + \
                                        RELAY_FIELDS['fingerprint'] + "' \
                                        target='_BLANK'>" + RELAY_FIELDS[value_name] + \
                                        "</a>"
                    if RELAY_FIELDS['isnamed']:
                        html_router_name = "<b>" + html_router_name + "</b>"
                    html_row_code = html_row_code + "<td id='col_relayName'>" + \
                                    html_router_name + "</td>"
            # Special Case: Icons
            elif column == 'Icons':
                html_icons = "<td id='col_relayIcons'>"
                for icon in ICONS:
                    if icon in current_columns:
                        value_icon = COLUMN_VALUE_NAME[icon]
                        html_icons = html_icons + RELAY_FIELDS[value_icon]
                html_icons = html_icons + "</td>"
                html_row_code = html_row_code + html_icons
            else:              
                html_row_code = html_row_code + "<td id='col_relay" + column + "'>" + \
                                RELAY_FIELDS[value_name] + "</td>"

        html_row_code = html_row_code + "</tr>"          
        html_table_rows.append(html_row_code)  
        
    return html_table_rows


def draw_bar_graph(xs, ys, labels, params):
    """
    Draws a bar graph, given data points, labels, and presentation
    parameters.

    @type xs: C{list}
    @param xs: The x values to be plotted.
    @type ys: C{list}
    @param ys: The y values to be plotted.
    @type labels: C{list} of C{string}
    @param labels: The labels to be used for each data point, where
        C{labels[i]} labels C{(xs[i], ys[i])}.
    @type params: C{dict} of C{string} and C{int}
    @param params: Parameters specifying how the graph is to be drawn.
        Params must contain the keys: WIDTH, HEIGHT, TOP_MARGIN,
        BOTTOM_MARGIN, LEFT_MARGIN, RIGHT_MARGIN, X_FONT_SIZE,
        Y_FONT_SIZE, LABEL_FONT_SIZE, FONT_WEIGHT, BAR_WIDTH,
        COLOR, LABEL_FLOAT, LABEL_ROT, and TITLE.
    @rtype: HttpResponse
    @return: The graph as specified by the parameters given.
    """
    ## Get the parameters from the params dictionary
    # Width and height of the graph in pixels
    WIDTH = params['WIDTH']
    HEIGHT = params['HEIGHT']
    # Space in pixels given around plot
    TOP_MARGIN = params['TOP_MARGIN']
    BOTTOM_MARGIN = params['BOTTOM_MARGIN']
    LEFT_MARGIN = params['LEFT_MARGIN']
    RIGHT_MARGIN = params['RIGHT_MARGIN']
    # Font sizes, in pixels
    X_FONT_SIZE = params['X_FONT_SIZE']
    Y_FONT_SIZE = params['Y_FONT_SIZE']
    LABEL_FONT_SIZE = params['LABEL_FONT_SIZE']
    # How many pixels above each bar the labels should be
    LABEL_FLOAT = params['LABEL_FLOAT']
    # How the labels should be presented
    LABEL_ROT = params['LABEL_ROT']
    # Font weight used for labels and titles
    FONT_WEIGHT = params['FONT_WEIGHT']
    BAR_WIDTH = params['BAR_WIDTH']
    COLOR = params['COLOR']
    # Title of graph
    TITLE = params['TITLE']

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

    # Draw the figure.
    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    # Plot the data.
    ax.bar(xs, ys, color=COLOR, width=BAR_WIDTH)

    # Label the height of each bar.
    label_float_ydist = ax.get_ylim()[1] * LABEL_FLOAT / (
                        HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)
    num_params = len(xs)
    for i in range(num_params):
        ax.text(xs[i] + (BAR_WIDTH / 2.0),
                ys[i] + (label_float_ydist), str(ys[i]),
                fontsize=LABEL_FONT_SIZE, horizontalalignment='center')

    x_index = matplotlib.numpy.arange(num_params)
    ax.set_xticks(x_index + (BAR_WIDTH / 2.0))
    ax.set_xticklabels(labels, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT, rotation=LABEL_ROT)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title(TITLE, fontsize='12', fontweight=FONT_WEIGHT)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

def draw_line_graph(fingerprint, bwtype, color, shade):
    """
    Draws a line graph with given data points and display parameters.

    @type fingerprint: C{string}
    @param fingerprint: The fingerprint of the router that the graph
        is to be drawn for.
    @type bwtype: C{string}
    @param bwtype: Either 'read' or 'written', depending on whether the
        graph to be drawn will be of recent read bandwidth or recent
        written bandwdith.
    @type color: C{string}
    @param color: The color to draw the line graph with.
    @type shade: C{string}
    @param shade: The color to shade under the line graph.
    @rtype: HttpResponse
    @return: The graph as specified by the parameters given.
    """
    # Width and height of the graph in pixels
    WIDTH = 480
    HEIGHT = 320
    # Space in pixels given around plot
    TOP_MARGIN = 42
    BOTTOM_MARGIN = 32
    LEFT_MARGIN = 98
    RIGHT_MARGIN = 5
    # Font sizes, in pixels
    X_FONT_SIZE = '8'
    Y_FONT_SIZE = '8'
    # Font weight used for labels and titles.
    FONT_WEIGHT = 'bold'

    # Set margins according to specification.
    matplotlib.rcParams['figure.subplot.left'] = \
            float(LEFT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.right'] = \
            float(WIDTH - RIGHT_MARGIN) / WIDTH
    matplotlib.rcParams['figure.subplot.top'] = \
            float(HEIGHT - TOP_MARGIN) / HEIGHT
    matplotlib.rcParams['figure.subplot.bottom'] = \
            float(BOTTOM_MARGIN) / HEIGHT

    last_hist = Bwhist.objects.filter(fingerprint=fingerprint)\
                .order_by('-date')[:1][0]

    if bwtype == 'Read':
        t_start, t_end, tr_list = last_hist.read
    elif bwtype == 'Written':
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

    start_time = recent_time - datetime.timedelta(
                 minutes=(15 * to_fill))
    end_time = start_time + datetime.timedelta(
               days=1) - datetime.timedelta(minutes=15)

    # If less than 96 entries in the array, get earlier entries.
    # If they don't exist, fill in the array with '0' values.
    if to_fill:
        day_before = last_hist.date - datetime.timedelta(days=1)

        try:
            day_before_hist = Bwhist.objects.get(\
                    fingerprint=fingerprint,
                    date=str(day_before))
            if bwtype == 'Read':
                y_start, y_end, y_list = day_before_hist.read
            elif bwtype == 'Written':
                y_start, y_end, y_list = day_before_hist.written
            y_list.extend([0] * (95 - y_end))
            y_list[0:0] = ([0] * y_start)

        except ObjectDoesNotExist:
            y_list = ([0] * 96)
        tr_list[0:0] = y_list[(-1 * to_fill):]

    width_inches = float(WIDTH) / 80
    height_inches = float(HEIGHT) / 80
    fig = Figure(facecolor='white', edgecolor='black',
                 figsize=(width_inches, height_inches), frameon=False)
    ax = fig.add_subplot(111)

    # Return bytes per second, not total bandwidth for 15 minutes.
    bps = map(lambda x: x / (15 * 60), tr_list)
    times = []
    for i in range(0, 104, 8):
        to_add_date = start_time + datetime.timedelta(minutes=(15 * i))
        to_add_str = "%0*d:%0*d" % (2, to_add_date.hour,
                                    2, to_add_date.minute)
        times.append(to_add_str)

    dates = range(96)

    # Draw the graph and give the graph a light shade underneath it.
    ax.plot(dates, bps, color=color)
    ax.fill_between(dates, 0, bps, color=shade)

    ax.set_xlabel("Time (GMT)", fontsize='12')
    ax.set_xticks(range(0, 104, 8))
    ax.set_xticklabels(times, fontsize=X_FONT_SIZE,
                       fontweight=FONT_WEIGHT)

    ax.set_ylabel("Bandwidth (bytes/sec)", fontsize='12')

    # Don't extend the y-axis to negative numbers, in any circumstance.
    ax.set_ylim(ymin=0)

    # Don't use scientific notation.
    ax.yaxis.major.formatter.set_scientific(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(Y_FONT_SIZE)
        tick.label1.set_fontweight(FONT_WEIGHT)

    ax.set_title("Average Bandwidth " + bwtype + " History:\n"
            + start_time.strftime("%Y-%m-%d %H:%M") + " to "
            + end_time.strftime("%Y-%m-%d %H:%M"), fontsize='12',
            fontweight=FONT_WEIGHT)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, ha="center")
    return response

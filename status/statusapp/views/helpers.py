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

FLAGS = set(('isauthority',
              'isbaddirectory',
              'isbadexit',
              'isexit',
              'isfast',
              'isguard',
              'ishibernating',
              'isnamed',
              'isstable',
              'isrunning',
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

# Dictionary of {NameInPlatform: NameOfTheIcon}
SUPPORTED_PLATFORMS = {'Linux': 'Linux',
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
                       'Dragon': 'DragonFly',
                      }


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
    return None


def get_platform(platform):
    """
    Method that searches in the platform string for the corresponding
    platform name and matching it to the corresponding icon name.

    @type platform: C{string}
    @param platform: A string, raw version of the platform of a relay.
    @rtype: C{string}
    @return: The icon name of the specific platform name.
    """
    for name in supported_platforms:
        if name in platform:
            return supported_platforms[name]
    return None


def generate_table_headers(current_columns, order_column_name, sort_order):
    """
    Generates a dictionary of {header_name: html_string_code}.

    @type current_columns: C{list}
    @param current_columns: A list of the columns that will be
        displayed on this session.
    @type order_column_name: C{string}
    @param order_column_name: A string - the name of the column that is
        currently ordering by.
    @type sort_order: C{string}
    @param sort_order: A string - the type of order
        (ascending/descending).
    @rtype: C{dict}, C{list}
    @return: Dictionary that contains the header name and the HTML code.
    @rtype: C{list}
    @return: List of the current columns that will be displayed.
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
                    html_table_headers[column] = "<th class='" + html_class +\
                                        "' id='" \
                                        + database_name + "'>" + display_name +\
                                        "</th>"
                    html_current_columns.append(column)
            else:
                html_table_headers[column] = "<th class='" + html_class + \
                                    "' id='" + database_name + "'>\
                                    <a class='sortLink' href='" + \
                                    sorting_link(sort_order, database_name) \
                                    + "'>" + display_name + " " + sort_arrow +\
                                    "</a></th>"
                html_current_columns.append(column)
    return html_table_headers, html_current_columns


def generate_table_rows(statusentries, current_columns,
        html_current_columns):
    """
    Generates a list of HTML strings. Each string represents a row in
    the main template table.

    @type statusentries: C{QuerySet}
    @param statusentries: A QuerySet of the statusentries.
    @type current_columns: C{list}
    @param current_columns: A list of the columns that will be displayed
        on this session.
    @type html_current_columns: C{list}
    @param html_current_columns: A list of the HTML string version of
        the current columns.

    @rtype: C{list}
    @return: List of HTML strings.
    """
    html_table_rows = []

    for relay in statusentries:
        #TODO: CLEAN THE CODE - QUERY ONLY ON THE NECESSARY COLUMNS
        #               AND THROW IN DICTIONARY AFTERWARDS!!!
        # Declarations made in order to avoid multiple queries.
        r_isbadexit = relay.isbadexit
        field_isbadexit = "<img src='/static/img/bg_" + \
                        ("yes" if r_isbadexit else "no") + \
                        ".png' width='12' height='12' alt='" + \
                        ("Bad Exit' title='Bad Exit'" \
                        if r_isbadexit else \
                        "Not a Bad Exit' title='Not a Bad Exit'") + ">"
        field_geoip = relay.geoip
        field_isnamed = relay.isnamed
        field_fingerprint = relay.fingerprint
        field_nickname = relay.nickname
        try:
            field_bandwidthobserved = str(kilobytes_ps(
                    relay.descriptorid.bandwidthobserved)) + " KB/s"
        except Descriptor.DoesNotExist:
            field_bandwidthobserved = "0 KB/s"
        try:
            field_uptime = str(days(relay.descriptorid.uptime)) + " d"
        except Descriptor.DoesNotExist:
            field_uptime = "0 d"
        r_address = relay.address
        field_address = "[<a href='details/" + r_address + \
                        "/whois'>" + r_address + "</a>]"
        field_published = str(relay.published)
        try:
            field_contact = contact(relay.descriptorid.rawdesc)
        except Descriptor.DoesNotExist:
            field_contact = ''
        r_isbaddir = relay.isbaddirectory
        field_isbaddirectory = "<img src='/static/img/bg_" + \
                        ("yes" if r_isbaddir else "no") + \
                        ".png' width='12' height='12' alt='" + \
                        ("Bad Directory' title='Bad Directory'" \
                        if r_isbaddir else "Not a Bad Directory' \
                        title='Not a Bad Directory'") + ">"
        field_isfast = "<img src='/static/img/status/Fast.png' \
                        alt='Fast Server' title='Fast Server'>" \
                        if relay.isfast else ""
        field_isv2dir = "<img src='/static/img/status/Dir.png' \
                        alt='Directory Server' title='Directory Server'>" \
                        if relay.isv2dir else ""
        field_isexit = "<img src='/static/img/status/Exit.png' \
                        alt='Exit Server' title='Exit Server'>" \
                        if relay.isexit else ""
        field_isguard = "<img src='/static/img/status/Guard.png' \
                        alt='Guard Server' title='Guard Server'>" \
                        if relay.isguard else ""
        field_isstable = "<img src='/static/img/status/Stable.png' \
                        alt='Stable Server' title='Stable Server'>" \
                        if relay.isstable else ""
        field_isauthority = "<img src='/static/img/status/Authority.png' \
                        alt='Authority Server' title='Authority Server'>" \
                        if relay.isauthority else ""
        try:
            r_platform = relay.descriptorid.platform
        except:
            r_platform = 'Not Available'
        r_os_platform = get_platform(r_platform)
        field_platform = "<img src='/static/img/os-icons/" + r_os_platform + \
                        ".png' alt='" + r_os_platform + "' title='" + \
                        r_platform + "'>" if r_os_platform else ""
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
                html_row_code = html_row_code + "<td id='col_relayName'> \
                                <a href='http://www.openstreetmap.org/?mlon="\
                                 + c_longitude + "&mlat=" + c_latitude + \
                                 "&zoom=6'><img src='/static/img/flags/" + \
                                 c_country + ".png' alt='" + c_country + \
                                 "' title='" + c_country + ":" + c_latitude +\
                                 ", " + c_longitude + "' border=0></a></td>"
            # Special Case: Router Name and Named
            elif column == 'Router Name':
                if 'Named' in current_columns:
                    html_router_name = "<a class='link' href='/details/" + \
                                        RELAY_FIELDS['fingerprint'] + "' \
                                        target='_BLANK'>" + \
                                        RELAY_FIELDS[value_name] + "</a>"
                    if RELAY_FIELDS['isnamed']:
                        html_router_name = "<b>" + html_router_name + "</b>"
                else:
                    html_router_name = "<a class='link' href='/details/" + \
                                        RELAY_FIELDS['fingerprint'] + "' \
                                        target='_BLANK'>" + \
                                        RELAY_FIELDS[value_name] + "</a>"
                html_row_code = html_row_code + "<td id='col_relayName'>"\
                                    + html_router_name + "</td>"
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
                html_row_code = html_row_code + "<td id='col_relay" + column \
                                + "'>" + RELAY_FIELDS[value_name] + "</td>"
        html_row_code = html_row_code + "</tr>"
        html_table_rows.append(html_row_code)

    return html_table_rows


def generate_query_list_options(query_options):
    """
    Generates the HTML version of each option in the Query List Options
    field.

    @type query_options: C{dict}
    @param query_options: A dictionary of the current query options.
    @rtype: C{list}
    @return: List of strings - each string represents the HTML version
        of an option.
    """
    # TODO: Finish this. It will clean up the
    # Advanced Query Options search.
    LIST_OPTIONS = {'Router Name': 'nickname',
                    'Fingerprint': 'fingerprint',
                    'Country Code': 'geoip',
                    'Bandwidth': 'bandwidthobserved',
                    'Uptime': 'uptime',
                    'Last Descriptor Published': 'published',
                    #'Hostname': 'hostname',
                    'IP Address': 'address',
                    'ORPort': 'orport',
                    'DirPort': 'dirport',
                    'Platform': 'platform',
                    'Contact': 'contact',
                    'Authority': 'isauthority',
                    'Bad Directory': 'isbaddirectory',
                    'Bad Exit': 'isbadexit',
                    'Exit': 'isexit',
                    'Fast': 'isfast',
                    'Guard': 'isguard',
                    'Hibernating': 'ishibernating',
                    'Named': 'isnamed',
                    'Stable': 'isstable',
                    'Valid': 'isvalid',
                    'Directory': 'isv2dir',
                   }

    html_query_list_options = []
    for option in LIST_OPTIONS:
        list_option = "<option value='" + LIST_OPTIONS[option] + "'"
        if ('sortListings' in query_options and \
                query_options['sortListings'] == LIST_OPTIONS[option]):
            list_option = list_option + " SELECTED>" + option + "</option>"
        else:
            list_option = list_option + ">" + option + "</option>"
        html_query_list_options.append(list_option)
    return html_query_list_options


def generate_query_input_options(query_options):
    """
    Generates the HTML version of each input option in the Required Flags
    feature.

    @type query_options: C{dict}
    @param query_options: A dictionary of the current query options.

    @rtype: C{list}
    @return: List of strings - each string represents the HTML version of
        an input option.
    """
    INPUT_OPTIONS = {'Authority': 'isauthority',
                    'Bad Directory': 'isbaddirectory',
                    'Bad Exit': 'isbadexit',
                    'Exit': 'isexit',
                    'Fast': 'isfast',
                    'Guard': 'isguard',
                    'Hibernating': 'ishibernating',
                    'Named': 'isnamed',
                    'Stable': 'isstable',
                    'Valid': 'isvalid',
                    'V2Dir': 'isv2dir',
                   }
    sorted_input_options = sorted(INPUT_OPTIONS.keys())
    html_query_input_options = []
    for option in sorted_input_options:
        input_option = "<td> " + option + ": </td>"
        input_string = ''
        for value in ['', 'yes', 'no']:
            input_string = input_string + "<input type='radio' \
                name='" + INPUT_OPTIONS[option] + "' value='" + value + "'"
            if not query_options and value == '':
                input_string = input_string + " CHECKED"
            if (INPUT_OPTIONS[option] in query_options and \
                    query_options[INPUT_OPTIONS[option]] == value):
                input_string = input_string + " CHECKED"
            input_string = input_string + " />" + ("Off" if value == '' else \
                value.capitalize())
        input_option = input_option + "<td>" + input_string + "</td>"
        html_query_input_options.append(input_option)
    return html_query_input_options

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

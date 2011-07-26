"""
Custom filters for the index page.
"""
# Django-specific import statements -----------------------------------
from django import template

# INIT Variables ------------------------------------------------------
FILTERED_NAME = {'Longitude': 'longitude',
                 'Latitude': 'latitude',
                 'Country Code': 'country',
                 'Router Name': 'nickname',
                 'Bandwidth': 'bandwidthkbps',
                 'Uptime': 'uptime',
                 'IP': 'address',
                 #'Hostname': 'hostname',
                 'Hibernating': 'hibernating',
                 'ORPort': 'orport',
                 'DirPort': 'dirport',
                 'BadExit': 'isbadexit',
                 'Named': 'isnamed',
                 'Exit': 'isexit',
                 'Authority': 'isauthority',
                 'Fast': 'isfast',
                 'Guard': 'isguard',
                 'Stable': 'isstable',
                 'V2Dir': 'isv2dir',
                 'Platform': 'platform',
                 'Fingerprint': 'fingerprint',
                 'LastDescriptorPublished': 'published',
                 'Contact': 'contact',
                 'BadDir': 'isbaddirectory',
                }

OS_LIST = set(('Linux', 'XP', 'Windows', 'Darwin', 'FreeBSD', 'NetBSD',
            'OpenBSD', 'SunOS', 'IRIX', 'Cygwin', 'Dragon'))


register = template.Library()

# Moved to HELPERS
@register.filter
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


@register.filter
def percent(a, b):
    """
    Return C{a / b} as a percent.

    @type a: C{int} or C{NoneType}
    @param a: The numerator of the percent.
    @type b: C{int}
    @param b: The denominator of the percent.
    @rtype: C{string}
    @return: C{a / b} as a percent as a string.
    """
    if a is None:
        return '0.00%'
    else:
        return '%0.2f%%' % (100.0 * a / b)


@register.filter
def key(d, key_name):
    """
    Return the value of a key in a dictionary.
    
    @type d: C{dict}
    @param d: The given dictionary.
    @type key_name: C{string}
    @param key_name: The given key.
    @rtype: C{value}
    @return: The value of the given key in the dictionary.
    """
    if key_name in d:
        return d[key_name]


@register.filter
def subtract(a, b):
    """
    Return the difference of two integers.

    @type a: C{int}
    @param a: The number to subtract from.
    @type b: C{int}
    @param b: The number to subtract.
    @rtype: C{int}
    @return: The difference of the two given integers.
    """
    return a - b
    

@register.filter
def field_value(relay_dict, key_name):
    """
    Return the value of a specific field of a relay.
    
    @type relay_dict: C{dict}
    @param relay_dict: Dictionary that contains all the fields for a specific
                    relay.
    @type key_name: C{string}
    @param key_name: The key of a field.
    @rtype: C{value}
    @return: The value of the given key in the relay dictionary.
    """
    return relay_dict[FILTERED_NAME[key_name]]


@register.filter
def get_os(platform):
    """
    Return the icon-name of the OS.
    
    @type platform: C{string}
    @param platform: A string that represents the platform of the relay.
    @rtype: C{string}
    @return: The icon-name version of the OS of the relay.
    """
    if platform:
        for os in OS_LIST:
            if os in platform:
                if os == 'Windows' and 'Server' in platform:
                    return 'WindowsServer'
                else:
                    return os
    return 'NotAvailable'

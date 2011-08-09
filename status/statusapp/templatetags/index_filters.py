"""
Custom filters for the index page.
"""
# Django-specific import statements -----------------------------------
from django import template

# TorStatus-specific import statements --------------------------------
import config

# INIT Variables ------------------------------------------------------
__OS_LIST = frozenset(('Linux', 'XP', 'Windows', 'Darwin', 'FreeBSD',
                     'NetBSD', 'OpenBSD', 'SunOS', 'IRIX', 'Cygwin',
                     'Dragon'))

register = template.Library()


@register.filter
def key(d, key_name):
    """
    Return the value of a key in a dictionary.

    Django provides something that looks like attribute lookups in
    templates that usually provide this functionality, but if the
    keys for the dictionary are generated dynamically, this
    attribute-like lookup (with syntax dict.key) does not function
    as desired.

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
    @param relay_dict: Dictionary that contains all the fields for a
        specific relay.
    @type key_name: C{string}
    @param key_name: The key of a field.
    @rtype: C{value}
    @return: The value of the given key in the relay dictionary.
    """
    return relay_dict[config.FILTERED_NAME[key_name]]


@register.filter
def get_os(platform):
    """
    Return the icon-name of the OS.

    @type platform: C{string}
    @param platform: A string that represents the platform of the
        relay.
    @rtype: C{string}
    @return: The icon-name version of the OS of the relay.
    """
    if platform:
        for os in __OS_LIST:
            if os in platform:
                if os == 'Windows' and 'Server' in platform:
                    return 'WindowsServer'
                else:
                    return os
    return 'NotAvailable'


@register.filter
def nospace(string):
    """
    Strip all space characters from a string.

    This function does not remove any other whitespace characters.

    >>> nospace('    t   hi \t s    has   n o \n s p    a ces   ')
    'thi\tshasno\nspaces'

    @type string: C{string}
    @param string: The string to remove all space characters from.
    @rtype: C{string}
    @return: The string provided, but with all spaces removed.
    """
    return string.replace(' ', '')

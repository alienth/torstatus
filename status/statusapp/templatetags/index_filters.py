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
    """
    return a - b
    
@register.filter
def filter_key(relay_dict, key_name):
    return relay_dict[FILTERED_NAME[key_name]]
    

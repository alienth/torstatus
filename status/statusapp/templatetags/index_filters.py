from django import template
import geoip

register = template.Library()

@register.filter
def kilobytes_ps(bytes_ps):
    """
    Convert a bandwidth value in bytes to a bandwidth value in kilobytes

    @type bytes_ps: C{int}, C{float}, C{long}, or C{string}
    @param bytes_ps: The bandwidth value, in bps.
    @rtype: C{int}
    @return: The bandwidth value in kbps.
    """
    return int(bytes_ps)/1024

@register.filter
def days(seconds):
    """
    Convert an duration in seconds to an uptime in days, rounding down.

    @type seconds: C{int}, C{float}, C{long}, or C{string}
    @param seconds: The duration in seconds. 
    @rtype: C{int}
    @return: The duration in days.
    """
    # As statusapp.views.details is written now, this value can 
    # be None sometimes.
    if (seconds == ''): 
        return 0
    else:
        return int(seconds)/86400

@register.filter
def getcountry(ip):
    return geoip.country(ip).lower()

@register.filter
def key(d, key_name):
    return d[key_name]

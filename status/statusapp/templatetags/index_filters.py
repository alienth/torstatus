"""
Custom filters for the index page.
"""
from django import template

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
    # As statusapp.views.details is written now, this value can
    # be None or an empty string sometimes.
    if (bytes_ps == '' or bytes_ps is None):
        return 0
    else:
        return int(bytes_ps) / 1024

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
    # be None or an empty string sometimes.
    if (seconds == '' or seconds is None):
        return 0
    else:
        return int(seconds) / 86400

@register.filter
def getcountry(location):
    #the location returned contains the country and the coordinates.
    return location.split(',')[0][1:3]

@register.filter
def percent(a, b):
    """
    Return C{a / b} as a percent.

    @type a: C{int}
    @param a: The numerator of the percent.
    @type b: C{int}
    @param b: The denominator of the percent.
    @rtype: C{string}
    @return: C{a / b} as a percent as a string.
    """
    return '%0.2f%%' % (100.0 * a / b)

@register.filter
def country(geoip):
    """
    Get the two-letter lowercase country code from a GeoIP string.

    @type geoip: C{string} or C{buffer}
    @param geoip: A string formatted as a tuple with entries country
        code, latitude, and longitude.
    @rtype: C{string}
    @return: The lowercase two-letter country code associated with
        C{geoip}.
    """
    return str(geoip).strip('()').split(',')[0].lower()

@register.filter
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


@register.filter
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

@register.filter
def key(d, key_name):
    return d[key_name]

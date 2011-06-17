# These filters should replace the {% widthratio %} tags used in index.html.
# kilobytes_ps doesn't function properly, however.

from django import template

register = template.Library()

@register.filter
def kilobytes_ps(bytes_ps):
    """
    Convert a bandwidth value in bytes to a bandwidth value in kilobytes
    """

    # As statusapp.views.details is written now, this value can 
    # be None sometimes.
    if (bytes_ps == None):
        return 0
    else:
        return int(bytes_ps)/1024

@register.filter
def days(seconds):
    """
    Convert an uptime in seconds to an uptime in days, rounding down
    """

    # As statusapp.views.details is written now, this value can 
    # be None sometimes.
    if (seconds == None): 
        return 0
    else:
        return int(seconds)/86000
from django import template

register = template.Library()

@register.filter
def kilobytes_ps(bytes_ps):
    """
    Convert a bandwidth value in bytes to a bandwidth value in kilobytes
    """

    # Issue: using in template yields error message:
    # Caught TypeError while rendering: int() argument must be a 
    # string or a number, not 'NoneType'
    return bytes_ps/1024

@register.filter
def days(seconds):
    """
    Convert an uptime in seconds to an uptime in days, rounding down
    """

    # Issue: using in template yields error message:
    # Caught TypeError while rendering: int() argument must be a 
    # string or a number, not 'NoneType'
    return seconds/86000



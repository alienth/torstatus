"""
Custom filters for the columnpreferences page.
"""
from django import template
import config

register = template.Library()


@register.filter
def movable(column_name):
    """
    Checks whether or not the passed column can be moved on the list.

    @rtype: C{boolean}
    @return: True if the column should be considered movable, False
        otherwise.
    """
    if column_name in config.NOT_MOVABLE_COLUMNS:
        return False;
    else:
        return True;

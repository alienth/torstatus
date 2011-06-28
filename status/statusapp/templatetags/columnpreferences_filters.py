"""
Custom filters for the columnpreferences page.
"""
from django import template

register = template.Library()

@register.filter
def movable(columnName):
    notMovableColumns = ["Named", "Exit", "Authority", "Fast", "Guard", "Stable", \
                        "Running", "Valid", "V2Dir", "Platform", "Hibernating"]
    if columnName in notMovableColumns:
        return False;
    else:
        return True;

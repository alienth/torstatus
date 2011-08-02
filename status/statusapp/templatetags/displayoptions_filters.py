"""
Custom filters for the columnpreferences page.
"""
from django import template

register = template.Library()

COLUMN_VALUE_NAME = {'Country Code': 'country',
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
                     'Directory': 'isv2dir',
                     'Platform': 'platform',
                     'Fingerprint': 'fingerprint',
                     'LastDescriptorPublished': 'published',
                     'Contact': 'contact',
                     'BadDir': 'isbaddirectory',
                    }

@register.filter
def movable(column_name):
    """
    Checks whether or not the passed column can be moved on the list.

    @rtype: C{boolean}
    """
    not_movable_columns = set(("Named", "Exit", "Authority", "Fast",
                               "Guard", "Stable", "Running", "Valid",
                               "V2Dir", "Platform", "Hibernating"))
    if column_name in not_movable_columns:
        return False;
    else:
        return True;

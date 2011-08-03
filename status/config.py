"""
Configuration and presentation variables for TorStatus.

@group Column Prefences/Defaults: L{AVAILABLE_COLUMNS}, L{DEFAULT_COLUMNS}
@group
"""

"""
C{frozenset} of all attributes of L{ActiveRelay}, since there
is no reason that a column should not be sortable.
"""

"""Columns not shown by default, but showable by selection"""
AVAILABLE_COLUMNS = ['Fingerprint', 'Last Descriptor Published',
                     'Contact', 'Bad Directory']

"""Columns shown by default"""
DEFAULT_COLUMNS = ['Country Code', 'Router Name', 'Bandwidth',
                   'Uptime', 'IP', 'Icons', 'ORPort',
                   'DirPort', 'Bad Exit', 'Named', 'Exit',
                   'Authority', 'Fast', 'Guard', 'Hibernating',
                   'Stable', 'V2Dir', 'Platform']
"""
Map titles of entries in curernt_columns to attribute names in
L{ActiveRelay}
"""
COLUMN_VALUE_NAME = {'Country Code': 'country',
                     'Router Name': 'nickname',
                     'Bandwidth': 'bandwidthkbps',
                     'Uptime': 'uptime',
                     'IP': 'address',
                     #'Hostname': 'hostname',
                     'Icons': 'icons',
                     'ORPort': 'orport',
                     'DirPort': 'dirport',
                     'Bad Exit': 'isbadexit',
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
                     'Last Descriptor Published': 'published',
                     'Contact': 'contact',
                     'Bad Directory': 'isbaddirectory',
                    }

CRITERIA = frozenset(('exact', 'iexact', 'contains', 'icontains',
                      'lt', 'gt', 'startswith', 'istartswith'))

"""
Default search column and order.

'Ascending' is denoted by a column name without a prefix,
while 'descending' is denoted by a '-' in front of the column name.
"""
DEFAULT_LISTING = 'nickname'

DISPLAYABLE_COLUMNS = frozenset(('Country Code', 'Router Name',
                                 'Bandwidth', 'Uptime', 'IP', 'Icons',
                                 'ORPort', 'DirPort', 'Bad Exit',
                                 'Fingerprint',
                                 'Last Descriptor Published',
                                 'Contact', 'Bad Directory'))

FILTER_OPTIONS = {'Authority': 'isauthority',
                  'Bad Directory': 'isbaddirectory',
                  'Bad Exit': 'isbadexit',
                  'Directory': 'isv2dir',
                  'Exit': 'isexit',
                  'Fast': 'isfast',
                  'Guard': 'isguard',
                  'Hibernating': 'ishibernating',
                  'HS Directory': 'ishsdir',
                  'Named': 'isnamed',
                  'Stable': 'isstable',
                  'Running': 'isrunning',
                  'Valid': 'isvalid',
                 }

"""
Define an order on the flags to be selected in display preferences.
"""
FILTER_OPTIONS_ORDER = ['Authority', 'Bad Directory', 'Bad Exit',
                        'Directory', 'Exit', 'Fast', 'Guard',
                        'Hibernating', 'HS Directory', 'Named',
                        'Stable', 'Running', 'Valid']

#### TOO SIMILAR TO COLUMN_VALUE_NAME ####
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
                 'Bad Exit': 'isbadexit',
                 'Named': 'isnamed',
                 'Exit': 'isexit',
                 'Authority': 'isauthority',
                 'Fast': 'isfast',
                 'Guard': 'isguard',
                 'Stable': 'isstable',
                 'V2Dir': 'isv2dir',
                 'Platform': 'platform',
                 'Fingerprint': 'fingerprint',
                 'Last Descriptor Published': 'published',
                 'Contact': 'contact',
                 'Bad Directory': 'isbaddirectory',
                }

"""
Names of attributes of L{ActiveRelay} objects that are either
C{True} or C{False}
"""
FLAGS = frozenset(('isauthority', 'isbaddirectory', 'isbadexit',
                   'isexit', 'isfast', 'isguard', 'ishibernating',
                   'ishsdir', 'isnamed', 'isstable', 'isrunning',
                   'isunnamed', 'isvalid', 'isv2dir', 'isv3dir'))

"""
Titles of columns for which icons are displayed
"""
ICONS = ('Hibernating', 'Fast', 'Exit', 'Valid', 'V2Dir', 'Guard',
         'Stable', 'Authority', 'Platform')

"""
Maximum number of routers to be viewable per page
"""
MAX_PP = 200

"""
Titles of relay attributes to be considered unmovable
"""
NOT_MOVABLE_COLUMNS = frozenset(("Named", "Exit", "Authority", "Fast",
                                 "Guard", "Hibernating", "Stable",
                                 "Running", "Valid", "V2Dir",
                                 "Platform"))

SEARCHES = frozenset(('fingerprint', 'nickname', 'country',
                      'bandwidthkbps', 'uptimedays', 'published',
                      'address', 'orport', 'dirport', 'platform'))

"""Map the title of a search criteria in the list of values of
SEARCH_OPTIONS_FIELDS_BOOLEANS to a criteria in CRITERIA"""
SEARCH_OPTIONS_BOOLEANS = {'Equals': 'exact',
                           'Equals (case sensitive)': 'exact',
                           'Equals (case insensitive)': 'iexact',
                           'Contains': 'contains',
                           'Contains (case insensitive)': 'icontains',
                           'Is Less Than': 'lt',
                           'Is Greater Than': 'gt',
                           'Starts With': 'startswith',
                           'Starts With (case insensitive)': 'istartswith',
                          }

"""Define an order by which the criteria will be presented on the
display options page"""
SEARCH_OPTIONS_BOOLEANS_ORDER = ['Equals',
                                 'Contains',
                                 'Is Less Than',
                                 'Is Greater Than']

SEARCH_OPTIONS_FIELDS = {'Fingerprint': 'fingerprint',
                         'Router Name': 'nickname',
                         'Country Code': 'country',
                         'Bandwidth (kb/s)': 'bandwidthkbps',
                         'Uptime (days)': 'uptimedays',
                         'Last Descriptor Published': 'published',
                         'IP Address': 'address',
                         #'Hostname': 'hostname',
                         'Onion Router Port': 'orport',
                         'Directory Server Port': 'dirport',
                         'Platform': 'platform',
                        }

SEARCH_OPTIONS_FIELDS_BOOLEANS = {
        'Fingerprint': ['Equals (case insensitive)',
                        'Contains (case insensitive)',
                        'Starts With (case insensitive)',],
        'Router Name': ['Equals (case insensitive)',
                        'Equals (case sensitive)',
                        'Contains (case insensitive)',
                        'Contains (case sensitive)',
                        'Starts With (case insensitive)',
                        'Starts With (case sensitive)',],
        'Country Code': ['Equals (case insensitive)',],
        'Bandwidth (kb/s)': ['Equals',
                             'Is Less Than',
                             'Is Greater Than',],
        'Uptime (days)': ['Equals',
                          'Is Less Than',
                          'Is Greater Than',],
        'Last Descriptor Published': ['Equals',
                                      'Is Less Than',
                                      'Is Greater Than',],
        'IP Address': ['Equals',
                       'Starts With',],
        'Onion Router Port': ['Equals',
                              'Is Less Than',
                              'Is Greater Than',],
        'Directory Server Port': ['Equals',
                                  'Is Less Than',
                                  'Is Greater Than',],
        'Platform': ['Contains (case insensitive)',],
       }

SEARCH_OPTIONS_FIELDS_ORDER = ['Fingerprint', 'Router Name',
                            'Country Code', 'Bandwidth (kb/s)',
                            'Uptime (days)', 'Last Descriptor Published',
                            'IP Address', 'Onion Router Port',
                            'Directory Server Port', 'Platform']

SORT_OPTIONS = {'Router Name': 'nickname',
                'Fingerprint': 'fingerprint',
                'Country Code': 'country',
                'Bandwidth': 'bandwidthkbps',
                'Uptime': 'uptime',
                'Last Descriptor Published': 'published',
                #'Hostname': 'hostname',
                'IP Address': 'address',
                'ORPort': 'orport',
                'DirPort': 'dirport',
                'Platform': 'platform',
                'Contact': 'contact',
                'Authority': 'isauthority',
                'Bad Directory': 'isbaddirectory',
                'Bad Exit': 'isbadexit',
                'V2Dir': 'isv2dir',
                'Exit': 'isexit',
                'Fast': 'isfast',
                'Guard': 'isguard',
                'Hibernating': 'ishibernating',
                'HS Directory': 'ishsdir',
                'Named': 'isnamed',
                'Stable': 'isstable',
                'Running': 'isrunning',
                'Valid': 'isvalid',
                }

SORT_OPTIONS_ORDER = ('Router Name', 'Fingerprint', 'Country Code',
                      'Bandwidth', 'Uptime',
                      'Last Descriptor Published', #'Hostname',
                      'IP Address', 'ORPort', 'DirPort',
                      'Platform', 'Contact', 'Authority',
                      'Bad Directory', 'Bad Exit', 'Directory',
                      'Exit', 'Fast', 'Guard', 'Hibernating',
                      'HS Directory', 'Named', 'Stable', 'Running',
                      'Valid')

"""Titles of columns to never display in CSV files"""
UNDISPLAYED_IN_CSVS = frozenset((#'Hostname',
                                 'Valid', 'Running', 'Named'))

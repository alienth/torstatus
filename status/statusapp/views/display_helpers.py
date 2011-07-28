"""
Helper variables, lists, dictionaries, used for a clean display in the template.
"""

# Advanced Search Template Helpers -----------------------------------
SORT_OPTIONS_ORDER = ['Router Name', 'Fingerprint', 'Country Code',
                    'Bandwidth', 'Uptime', 'Last Descriptor Published',
                    'Hostname', 'IP Address', 'ORPort', 'DirPort',
                    'Platform', 'Contact', 'Authority', 'Bad Directory',
                    'Bad Exit', 'Directory', 'Exit', 'Fast', 'Guard',
                    'Hibernating', 'HS Directory', 'Named',
                    'Stable', 'Running', 'Valid',]

SORT_OPTIONS = {'Router Name': 'nickname',
                'Fingerprint': 'fingerprint',
                'Country Code': 'country',
                'Bandwidth': 'bandwidthkbps',
                'Uptime': 'uptime',
                'Last Descriptor Published': 'published',
                'Hostname': 'hostname',
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

SEARCH_OPTIONS_FIELDS_ORDER = ['Fingerprint', 'Router Name',
                            'Country Code', 'Bandwidth (kb/s)',
                            'Uptime (days)', 'Last Descriptor Published',
                            'IP Address', 'Onion Router Port',
                            'Directory Server Port', 'Platform']
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

SEARCH_OPTIONS_BOOLEANS_ORDER = ['Equals',
                                 'Contains',
                                 'Is Less Than',
                                 'Is Greater Than']
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

FILTER_OPTIONS_ORDER = ['Authority', 'BadDirectory', 'BadExit',
                        'Directory', 'Exit', 'Fast', 'Guard',
                        'Hibernating', 'HS Directory', 'Named',
                        'Stable', 'Running', 'Valid']

FILTER_OPTIONS = {'Authority': 'isauthority',
                  'BadDirectory': 'isbaddirectory',
                  'BadExit': 'isbadexit',
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
# Dictionary that maps the declared variables to variables
# in actual code.
ADVANCED_SEARCH_DECLR = {'sort_options_order': SORT_OPTIONS_ORDER,
                         'sort_options': SORT_OPTIONS,
                         'search_options_fields_order':
                                    SEARCH_OPTIONS_FIELDS_ORDER,
                         'search_options_fields': SEARCH_OPTIONS_FIELDS,
                         'search_options_fields_booleans': 
                                    SEARCH_OPTIONS_FIELDS_BOOLEANS,
                         'search_options_booleans_order':
                                    SEARCH_OPTIONS_BOOLEANS_ORDER,
                         'search_options_booleans': SEARCH_OPTIONS_BOOLEANS,
                         'filter_options_order': FILTER_OPTIONS_ORDER,
                         'filter_options': FILTER_OPTIONS,
                        }


# Index Template Helpers ---------------------------------------------


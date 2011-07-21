"""
Helper variables, lists, dictionaries, used for a clean display in the template.
"""

# Advanced Search Template -----------------------------------
SORT_OPTIONS_ORDER = ['Router Name', 'Fingerprint', 'Country Code',
                    'Bandwidth', 'Uptime', 'Last Descriptor Published',
                    'Hostname', 'IP Address', 'ORPort', 'DirPort',
                    'Platform', 'Contact', 'Authority', 'Bad Directory',
                    'Bad Exit', 'Exit', 'Fast', 'Guard', 'Hibernating',
                    'Named', 'Stable', 'Running', 'Valid', 'Directory']
SORT_OPTIONS = {'Router Name': 'nickname',
                'Fingerprint': 'fingerprint',
                'Country Code': 'geoip',
                'Bandwidth': 'bandwidthobserved',
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
                'Exit': 'isexit',
                'Fast': 'isfast',
                'Guard': 'isguard',
                'Hibernating': 'ishibernating',
                'Named': 'isnamed',
                'Stable': 'isstable',
                'Running': 'isrunning',
                'Valid': 'isvalid',
                'Directory': 'isv2dir',
               }

SEARCH_OPTIONS_FIELDS_ORDER = ['Fingerprint', 'Router Name',
                            'Country Code', 'Bandwidth (kb/s)',
                            'Uptime (days)', 'Last Descriptor Published',
                            'IP Address', 'Hostname', 'Onion Router Port',
                            'Directory Server Port', 'Platform']
SEARCH_OPTIONS_FIELDS = {'Fingerprint': 'fingerprint',
                         'Router Name': 'nickname',
                         'Country Code': 'geoip',
                         'Bandwidth (kb/s)': 'bandwidthobserved',
                         'Uptime (days)': 'uptime',
                         'Last Descriptor Published': 'published',
                         'IP Address': 'address',
                         'Hostname': 'hostname',
                         'Onion Router Port': 'orport',
                         'Directory Server Port': 'dirport',
                         'Platform': 'platform',
                        }

SEARCH_OPTIONS_BOOLEANS_ORDER = ['Equals', 'Contains', 'Is Less Than',
                                'Is Greater Than']
SEARCH_OPTIONS_BOOLEANS = {'Equals': 'equals',
                           'Contains': 'contains',
                           'Is Less Than': 'less',
                           'Is Greater Than': 'greater',
                          }
                            
FILTER_OPTIONS_ORDER = ['Authority', 'BadDirectory', 'BadExit', 'Exit',
                        'Fast', 'Guard', 'Hibernating', 'Named', 'Stable', 
                        'Running', 'Valid', 'V2Dir']

FILTER_OPTIONS = {'Authority': 'isauthority',
                  'Bad Directory': 'isbaddirectory',
                  'Bad Exit': 'isbadexit',
                  'Exit': 'isexit',
                  'Fast': 'isfast',
                  'Guard': 'isguard',
                  'Hibernating': 'ishibernating',
                  'Named': 'isnamed',
                  'Stable': 'isstable',
                  'Running': 'isrunning',
                  'Valid': 'isvalid',
                  'V2Dir': 'isv2dir',
                 }
# Dictionary that maps the declared variables to variables in actual code.
ADVANCED_SEARCH_DECLR = {'sort_options_order': SORT_OPTIONS_ORDER,
                         'sort_options': SORT_OPTIONS,
                         'search_options_fields_order': 
                                    SEARCH_OPTIONS_FIELDS_ORDER,
                         'search_options_fields': SEARCH_OPTIONS_FIELDS,
                         'search_options_booleans_order':
                                    SEARCH_OPTIONS_BOOLEANS_ORDER,
                         'search_options_booleans': SEARCH_OPTIONS_BOOLEANS,
                         'filter_options_order': FILTER_OPTIONS_ORDER,
                         'filter_options': FILTER_OPTIONS,
                        }


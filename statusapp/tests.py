"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from statusapp.views import _is_ip_in_subnet

__test__ = {"doctest": """

>>> _is_ip_in_subnet('0.0.0.0', '0.0.0.0/16')
True
>>> _is_ip_in_subnet('0.0.255.255', '0.0.0.0/16')
True
>>> _is_ip_in_subnet('0.1.0.0', '0.0.0.0/16')
False"""}


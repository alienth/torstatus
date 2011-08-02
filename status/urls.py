"""
The URLCONF for the base TorStatus application.

This URLCONF simply defers to the URLCONF found in statusapp.urls.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('statusapp.urls')),
)

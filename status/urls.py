"""
The URLCONF for the base TorStatus application.

This URLCONF simply defers to the URLCONF found in statusapp.urls.
"""

from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings


urlpatterns = patterns('',
    (r'^', include('newstatus.urls')),
    (r'^', include('statusapp.urls')),
)

from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings


urlpatterns = patterns('',
    (r'^', include('statusapp.urls')),
)

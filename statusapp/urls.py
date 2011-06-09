from django.conf.urls.defaults import *

from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^$', 'statusapp.views.index'),
    (r'^(?P<fingerprint>\w{40})/details/', 'statusapp.views.details'),
    (r'^flags/(?P<country_code>\w\w).gif', 'statusapp.views.displayFlag'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
)

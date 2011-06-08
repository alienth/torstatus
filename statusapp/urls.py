from django.conf.urls.defaults import *

from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^$', 'statusapp.views.index'),
    (r'^flags/(?P<country_code>\w\w).gif', 'statusapp.views.displayFlag'),
    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}) # Needs to be whole path


    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

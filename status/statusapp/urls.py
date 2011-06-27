from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^$', 'statusapp.views.index'),
    (r'^details/(?P<descriptor_fingerprint>\w{40})', 'statusapp.views.details'),
    (r'^details/(?P<fingerprint>\w{40})/graph1.png', 'statusapp.views.graph1'),
    (r'^details/(?P<fingerprint>\w{40})/graph2.png', 'statusapp.views.graph2'),
    (r'^flags/(?P<country_code>\w\w).gif', 'statusapp.views.displayFlag'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', \
            {'document_root': settings.MEDIA_ROOT}),
    (r'^exit-node-query/', 'statusapp.views.exitnodequery'),
    (r'^network-statistic-graphs/', 'statusapp.views.networkstatisticgraphs'),
    (r'^column-preferences/', 'statusapp.views.columnpreferences'),
    (r'^Tor-Query-Export.csv','statusapp.views.unruly_passengers_csv'),
    #Eventually have to make own function to send appropriate stuff
    (r'^Tor-IP-List-All.csv','statusapp.views.unruly_passengers_csv'),#ditto
    (r'^Tor-IP-List-Exit.csv','statusapp.views.unruly_passengers_csv'),#ditto
    (r'^custom/$', 'statusapp.views.custom_index'),
    (r'^details/\w{40}/graph1.png', 'statusapp.views.graph1'),
    (r'^details/\w{40}/graph2.png', 'statusapp.views.graph2'),
    #Figure out how to make a method or methods that is capable of
    #taking all the custom parameters and generate a custom index page.
)

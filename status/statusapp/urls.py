from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^$', 'statusapp.views.index'),
    (r'^details/(?P<fingerprint>\w{40})/readhist.png', 'statusapp.views.readhist'),
    (r'^details/(?P<fingerprint>\w{40})/writehist.png', 'statusapp.views.writehist'),
    (r'^details/(?P<fingerprint>\w{40})', 'statusapp.views.details'),
    (r'^flags/(?P<country_code>\w\w).gif', 'statusapp.views.displayFlag'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', \
            {'document_root': settings.MEDIA_ROOT}),
    (r'^exit-node-query/', 'statusapp.views.exitnodequery'),
    (r'^network-statistic-graphs/aggregatesummary.png', 'statusapp.views.aggregatesummary'),
    (r'^network-statistic-graphs/', 'statusapp.views.networkstatisticgraphs'),
    (r'^column-preferences/', 'statusapp.views.columnpreferences'),
    (r'^Tor-Query-Export.csv','statusapp.views.current_results_csv'),
    #Eventually have to make own function to send appropriate stuff
    (r'^Tor-IP-List-All.csv','statusapp.views.all_ip_csv'),#ditto
    (r'^Tor-IP-List-Exit.csv','statusapp.views.all_exit_csv'),#ditto
    (r'^custom/$', 'statusapp.views.custom_index'),
    #Figure out how to make a method or methods that is capable of
    #taking all the custom parameters and generate a custom index page.
)

from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'statusapp.views.index'),
    (r'^details/(?P<fingerprint>\w{40})$',
        'statusapp.views.details'),
    (r'^flags/(?P<country_code>\w\w).gif$',
        'statusapp.views.displayFlag'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    (r'^exit-node-query/$', 'statusapp.views.exitnodequery'),
    (r'^network-statistic-graphs/$',
        'statusapp.views.networkstatisticgraphs'),
    (r'^column-preferences/$', 'statusapp.views.columnpreferences'),
    (r'^Tor-Query-Export.csv$', 'statusapp.views.unruly_passengers_csv'),
    (r'^Tor-IP-List-All.csv$', 'statusapp.views.unruly_passengers_csv'),
    (r'^Tor-IP-List-Exit.csv$', 'statusapp.views.unruly_passengers_csv'),
    (r'^details/(?P<fingerprint>\w{40})/readhist.png$',
        'statusapp.views.readhist'),
    (r'^details/(?P<fingerprint>\w{40})/writehist.png$',
        'statusapp.views.writehist'),
    (r'^network-statistic-graphs/aggregatesummary.png$',
        'statusapp.views.aggregatesummary'),
)

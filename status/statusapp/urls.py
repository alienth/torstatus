"""
The URLCONF for the statusapp.
"""

from django.conf.urls.defaults import *
from django.views.static import *
from django.conf import settings
from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
    # Splash page
    (r'^$', 'statusapp.views.pages.splash'),

    # Search
    (r'^advanced-search$', 'statusapp.views.pages.advanced_search'),

    # Unpaged Index and related pages
    (r'^display-options/$', 'statusapp.views.pages.display_options'),
    (r'^exit-node-query/$', 'statusapp.views.pages.exitnodequery'),

    # Media Files
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

    # Details Page
    (r'^details/(?P<fingerprint>\w{40})$', 'statusapp.views.pages.details'),
    # Details Page Graphs
    (r'^details/(?P<fingerprint>\w{40})/readhist.png$',
        'statusapp.views.graphs.readhist'),
    (r'^details/(?P<fingerprint>\w{40})/writehist.png$',
        'statusapp.views.graphs.writehist'),

    # Whois Page
    (r'^details/(?P<address>.{7,15})/whois$',
        'statusapp.views.pages.whois'),

    # Network Statistic Graphs Page
    (r'^network-statistic-graphs/$',
        'statusapp.views.pages.networkstatisticgraphs'),
    # Network Statistic Graphs .png
    (r'^network-statistic-graphs/aggregatesummary.png$',
        'statusapp.views.graphs.aggregatesummary'),
    (r'^network-statistic-graphs/bycountrycode.png$',
        'statusapp.views.graphs.bycountrycode'),
    (r'^network-statistic-graphs/exitbycountrycode.png$',
        'statusapp.views.graphs.exitbycountrycode'),
    (r'^network-statistic-graphs/bytimerunning.png$',
        'statusapp.views.graphs.bytimerunning'),
    (r'^network-statistic-graphs/byobservedbandwidth.png$',
        'statusapp.views.graphs.byobservedbandwidth'),
    (r'^network-statistic-graphs/byplatform.png$',
        'statusapp.views.graphs.byplatform'),
    (r'^network-statistic-graphs/networktotalbw.png$',
        'statusapp.views.graphs.networktotalbw'),

    # CSV Files
    (r'^tor-query-export.csv$', 'statusapp.views.csvs.current_results_csv'),

    # Index and related pages
    (r'^index/sort/(?P<sort_filter>\w*)$', 'statusapp.views.pages.index'),
    (r'^index/$', 'statusapp.views.pages.index', {'sort_filter': ''}),
    (r'^reset_index/$', 'statusapp.views.pages.index_reset'),
)

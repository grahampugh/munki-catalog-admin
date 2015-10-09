from django.conf.urls import patterns, include, url

urlpatterns = patterns('catalogs.views',
    url(r'^$', 'catalog_view'),
    url(r'^(?P<catalog_name>[^/]+)/$', 'catalog_view'),
    url(r'^(?P<catalog_name>[^/]+)/(?P<item_index>\d+)/$', 'item_detail'),
	url(r'^test/*$', 'test'),
)
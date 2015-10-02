from django.conf.urls import patterns, include, url

urlpatterns = patterns('manifests.views',
    url(r'^$', 'index', name="mdo-catalogs"),
    url(r'^new$', 'new'),
    url(r'^copymanifest$', 'copymanifest'),
    url(r'^delete/(?P<manifest_name>[^/]+)/$', 'delete'),
    url(r'^#(?P<manifest_name>.+)/$', 'index', name="mdo-catalogs"),
    url(r'^view/(?P<manifest_name>[^/]+)/$', 'view'),
    url(r'^detail/(?P<manifest_name>[^/]+)$', 'detail'),
)
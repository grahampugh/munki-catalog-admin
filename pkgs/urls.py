from django.conf.urls import patterns, include, url

urlpatterns = patterns('pkgs.views',
	url(r'^$', 'index', name="mdo-catalogs"),
	url(r'^index/*$', 'index', name="mdo-catalogs"),
	url(r'^confirm/*$', 'confirm'),
	url(r'^done/*$', 'done'),
	url(r'^deleted/*$', 'deleted'),
)
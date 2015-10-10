from django.conf.urls import patterns, include, url

urlpatterns = patterns('pkgs.views',
	url(r'^index/*$', 'index'),
	url(r'^confirm/*$', 'confirm'),
	url(r'^done/*$', 'done'),
	url(r'^deleted/*$', 'deleted'),
	url(r'^$', 'index'),
)
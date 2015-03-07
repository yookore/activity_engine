from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'activity_engine.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'feed_engine.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<username>[\w\d]+)/generate/$', 'feed_engine.views.generate_activities', name='gen_activities'),
    url(r'^(?P<username>[\w\d]+)/activities/(?P<pointer>(next|previous))/(?P<nextset>[\w\d\-]+)/$', 'feed_engine.views.get_activities', name='get_activities'),
    url(r'^(?P<username>[\w\d]+)/activities/$', 'feed_engine.views.get_activities', name='get_activities'),
    url(r'^activities/add$', 'feed_engine.views.create_activity', name='add_activity')
)

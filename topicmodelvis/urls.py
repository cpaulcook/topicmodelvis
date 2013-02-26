from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Since this admin should be app-specific, I'm including it as part 
    # of corpora.
    # It also needs to go first or else it matches with one of the 
    # corpus patterns.
    url(r'^admin/', include(admin.site.urls)),
        
    # Rest of url patterns:
    url(r'^corpora/$', 'sesvis.views.corpora'),
    url(r'^corpora/(?P<corpus_name>\w+)/$', 'sesvis.views.corpus'),
    url(r'^corpora/(?P<corpus_name>\w+)/topic/(?P<corpus_topic_id>\d+)$', 
        'sesvis.views.topic'),
    url(r'^corpora/(?P<corpus_name>\w+)/subcorpus/(?P<subcorpus_name>\w+)$', 
        'sesvis.views.subcorpus'),
    url(r'^corpora/(?P<corpus_name>\w+)/doc/(?P<document_title>[a-zA-z0-9\.]+)$',
        'sesvis.views.document'),

    # Examples:
    # url(r'^$', 'topicmodelvis.views.home', name='home'),
    # url(r'^topicmodelvis/', include('topicmodelvis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
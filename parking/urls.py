from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    #url(r'^$', 'parking.views.home', name='home'),
    #url(r'^parking/', include('parking.foo.urls')),

    url(r'^crawler/', include('crawler.urls')),

    url(r'^tags/', include('taggittokenfield.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),

    # admin
    #url(r'^grappelli/', include('grappelli.urls')),
    url(r'^doc/', include('django.contrib.admindocs.urls')),
    url(r'^', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
                            (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT}),
    )


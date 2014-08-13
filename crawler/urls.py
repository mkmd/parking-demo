# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(
        r'^rules/',
        include(patterns(
            'crawler.views',
            url(r'^(?P<parser>\d+)/$', 'parser_rules', name='parser-rules'),
            url(r'^(?P<engine>[^/]+)/$', 'engine_rules', name='parser-rules'),
            url(r'^(?P<parser>\d+)/(?P<engine>[^/]+)/$', 'rules', name='parser-rules'),
        ))
    )
)
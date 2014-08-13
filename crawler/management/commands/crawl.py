# -*- coding: utf-8 -*-

import logging
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals

from crawler.models import SiteSlice, Article, Category
from crawler.bot import spider_project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<bot name>'
    help = '''Manages the parsing sites.
           Sites are stored in a database that is managed by
           administrative panel in "/admin/parser/urlset/".'''

    option_list = BaseCommand.option_list + (
        make_option('--crawl',
                    action='store_true',
                    dest='crawl',
                    default=True,
                    help='Starts the sites parsing process.'
        ),
        make_option('--check',
                    action='store_true',
                    dest='check',
                    default=False,
                    help='Check the integrity of parsed data.'),
    )

    def handle(self, *args, **options):
        if options['check']:
            self.check()
        elif options['crawl']:
            sites = SiteSlice.active.all()
            self.crawl(sites)

    @classmethod
    def check(cls):
        """Check the integrity"""
        pass

    @classmethod
    def crawl(cls, sites):
        stat = {"spiders": 0}

        def soft_stop_reactor():
            stat["spiders"] -= 1
            if not stat["spiders"]:
                reactor.stop()

        for site in sites:
            try:
                spider = site.parser.spider(site)
            except (NotImplementedError, ObjectDoesNotExist):
                logger.error(_('Spider not implemented for "%s" site', site.label))
            else:
                stat["spiders"] += 1
                with spider_project(spider) as settings:
                    crawler = Crawler(settings)
                    crawler.signals.connect(soft_stop_reactor, signal=signals.spider_closed)  # reactor.stop
                    crawler.configure()
                    crawler.crawl(spider)
                    crawler.start()

        logfile = open('crawl.log', 'w')
        log_observer = log.ScrapyFileLogObserver(logfile, level=logging.INFO)
        log_observer.start()

        # the script will block here until the spider_closed signal was sent
        reactor.run()
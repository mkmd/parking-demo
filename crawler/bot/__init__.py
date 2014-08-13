# -*- coding: utf-8 -*-

import os
import sys
import logging
import itertools
import json
from contextlib import contextmanager
from scrapy.utils.conf import init_env
from scrapy.utils.project import get_project_settings
from scrapy.spidermanager import SpiderManager
from scrapy.spider import BaseSpider as ScrapyBaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
#from scrapy.utils.misc import walk_modules
#from scrapy.utils.spider import iter_spider_classes

from contrib.utils import load_class

logger = logging.getLogger(__name__)


@contextmanager
def spider_project(path_or_spider):
    cur_dir = os.path.abspath(os.curdir)
    mod_path = lambda cls: os.path.dirname(sys.modules[cls.__class__.__module__].__file__)
    path = mod_path(path_or_spider) if isinstance(path_or_spider, ScrapyBaseSpider) else path_or_spider

    os.chdir(path)
    init_env()
    try:
        yield get_project_settings()
    finally:
        os.chdir(cur_dir)


def discover_spiders():
    for project in _discover_spider_projects():
        with spider_project(project) as settings:
            manager = SpiderManager.from_settings(settings)
            for spider in manager._spiders.itervalues():
                yield spider


def load_spider(engine):
    _enable_spider_project(engine)
    try:
        return load_class(engine)
    except ImportError:
        logger.error('Module "%s" was not found', engine)
        raise

    #from django.utils.importlib import import_module
    #bits = DEFAULT_SETTINGS['SLUG_TRANSLITERATOR'].split(".")
    #module = import_module(".".join(bits[:-1]))
    #DEFAULT_SETTINGS['SLUG_TRANSLITERATOR'] = getattr(module, bits[-1])


def load_spider_rule_template(shortcut):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'rule.' + shortcut + '.json')
    return json.load(open(template_path, 'r'))  # encoding='utf-8'  # open(template_path, 'r').read()


def _discover_spider_projects():
    bot_dir = os.path.dirname(__file__)
    paths = [os.path.join(bot_dir, project)
             for project in os.listdir(bot_dir) if project != 'templates']
    return itertools.ifilter(os.path.isdir, paths)


def _enable_spider_project(package_path):
    try:
        package_path = os.path.join(os.path.dirname(__file__), package_path.split('.')[0])
        if not os.path.exists(package_path) or package_path in sys.path:
            raise IOError()
    except (IndexError, IOError):
        return False
    else:
        sys.path.append(package_path)
        return True


class EmptyLinkExtractor():
    """Dummy extractor"""

    def extract_links(self, response):
        return []


class BaseSpider(CrawlSpider):
    def __init__(self, site, **opts):
        self.site = site
        self.init_rules(opts)

        super(BaseSpider, self).__init__(**opts)

    @classmethod
    def init_rules(cls, opts):
        """Default rules initialization"""
        def make_extractor(opts):
            le = SgmlLinkExtractor if opts.get('link_extractor', None) else EmptyLinkExtractor
            le_opts = opts.pop('link_extractor', {})
            return le(**le_opts)

        def make_rule(opts):
            return Rule(make_extractor(opts), **opts)

        try:
            opts['rules'] = map(make_rule, opts['rules'])
        except KeyError:
            pass



# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import os
#from collections import defaultdict
from django.db import IntegrityError
from django.db.models import F
from django.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

from crawler.models import SiteSlice, Category, Summary


class StoreArticle(object):
    def __init__(self):
        self.counter = {"parsed": 0, "warn": 0, "error": 0}
        self.site = None

    def open_spider(self, spider):
        self.site = SiteSlice.objects.get(pk=spider.site)

    def close_spider(self, spider):
        summary, created = Summary.objects.get_or_create(site=self.site)
        summary.parsed_n_articles = self.counter["parsed"]
        summary.warns = self.counter["warn"]  # F('parsed_n_articles') + 1
        summary.errors = self.counter["error"]
        summary.save()

    def process_item(self, item, spider):
        try:
            item['site'] = self.site

            if item['images']:
                self._update_image_paths(item)

            article = item.save()
        except IntegrityError as e:
            self.counter["warn"] += 1
            log.msg('Met duplicates article: %s' % item["url"], level=log.WARNING)
        except BaseException as e:
            self.counter["error"] += 1
            msg = 'Unknown error during the item saving: %s' % item["url"]
            log.msg(msg, level=log.ERROR)
            raise DropItem(msg)
        else:
            self.counter["parsed"] += 1
            return item

    def _update_image_paths(self, item):
        def make_url(path):
            return os.path.join(settings.MEDIA_DOMAIN, settings.MEDIA_URL, path)

        for image in item["images"]:
            if image['path']:
                item["body_text"] = item["body_text"].replace(image['url'], make_url(image['path']))

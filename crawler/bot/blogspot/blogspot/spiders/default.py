# -*- coding: utf-8 -*-

import logging
from scrapy.exceptions import CloseSpider, IgnoreRequest  # DontCloseSpider
from scrapy.http.request import Request
from scrapy import log

from blogspot.items import ArticleChecker, ArticleLoader
from crawler.bot import BaseSpider as BotBaseSpider


class DefaultSpider(BotBaseSpider):
    name = 'blogspot'  # warn: don't remove - "load_spider" based on this attribute

    def parse_link(self, response, **search):
        yield ArticleLoader(search=search, response=response).load_item()

    #def parse(self, response):
    #    pass

    # parse the entry (index) page
    def parse_start_url(self, response, **link):
        def get_self_rule():
            i, rule = next((i, item) for i, item in enumerate(self.rules) if item.callback == 'parse_start_url')
            self._rules.pop(i)
            self.rules.pop(i)
            return rule

        def get_item_rule():
            i, rule = next((i, item) for i, item in enumerate(self.rules) if item.callback == 'parse_link')
            self._rules.pop(i)
            self.rules.pop(i)
            return rule

        rule = get_self_rule()

        try:
            fresh_urls, exists_url = ArticleChecker.from_page(response, rule.cb_kwargs).get_fresh_urls()
            if fresh_urls:
                item_rule = get_item_rule()

                def exec_parse_item(response):
                    return next(self.parse_link(response, **item_rule.cb_kwargs))

                self._rules = []
                self.rules = []
                return [Request(url, callback=exec_parse_item) for url in fresh_urls]
            elif exists_url:
                raise ValueError('All articles on the start page "%s" already exists in the database' % response.url)
        except ValueError as e:
            raise CloseSpider(str(e))
        except IndexError:
            return

# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#__all__ = []

# from functools import partial
from os.path import join, basename
import re
# from string import maketrans
import locale
from urlparse import urlparse, urlunparse  # , urljoin
from datetime import datetime

import calendar
from dateutil.parser import parse as parse_date
from contextlib import contextmanager
from django.conf import settings
from django.utils.timezone import utc
from scrapy.item import Item, Field
from scrapy.contrib.djangoitem import DjangoItem
from scrapy.selector import Selector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Join, Compose, TakeFirst  # MapCompose

from crawler.models.article import Article, Category

@contextmanager
def tmp_locale(name='ru_RU.utf-8'):
    cur_loc = locale.getlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, name)
    try:
        yield
    finally:
        locale.setlocale(locale.LC_ALL, cur_loc)


class TextTool(object):
    # todo: use __slots__
    __slots__ = ['strip', 'normalize', 'cut_substring', 'trim_number', 'first_line']

    def __init__(self, strip=True, normalize=False, first_line=False, cut_substring='', trim_number=0):
        self.strip = strip
        self.normalize = normalize
        self.cut_substring = cut_substring
        self.trim_number = trim_number
        self.first_line = first_line

    def __call__(self, value):
        def process(val):
            if not val:
                return val

            if self.strip:
                val = self.get_stripped(val)
            if self.first_line:
                val = self.get_first_line(val)
            if self.normalize:
                val = self.get_normalized(val)
            if self.cut_substring:
                val = self.get_clipped(val, self.cut_substring)
            if self.trim_number:
                val = self.get_trimmed(val, self.trim_number)

            return val

        if type(value) is list:
            return map(process, value)
        return process(value)

    @classmethod
    def get_stripped(cls, value):
        return value.strip(' \n\t' + unichr(160))

    @classmethod
    def get_normalized(cls, value):
        return value.replace('\r', '').replace('\n', '') \
            .replace('\t', '').replace('  ', ' ')  # re.sub('\s\s', ' ', value)

    @classmethod
    def get_clipped(cls, value, substring):
        # todo: maketrans
        return value if not substring else value.replace(substring, '')  # unicode

    @classmethod
    def get_trimmed(cls, value, number):
        return value if not number else value[:int(number)]

    @classmethod
    def get_first_line(cls, value):
        try:
            value.replace('\r', '\n').index('\n')
        except ValueError:
            return value
        else:
            return cls.get_stripped(value.split('\n').pop(0))


def generate_month_table():
    months = calendar.month_name[1:]
    with tmp_locale():
        return zip(calendar.month_abbr[1:], months)


class ParseDate(object):
    __slots__ = ('default', 'patch_table')

    month_table = generate_month_table()

    def __init__(self, default=None, patch_table=None):
        self.default = default or self.default_date()
        self.patch_table = patch_table

    def __call__(self, value):
        if type(value) is list:
            return filter(None, map(self._get, value))
        else:
            return self._get(value)

    def normalize(self, value):
        """
        Translate all month occurrence by map "month abbreviation: month name".
        Month name is safe because encoded in ascii.
        """
        def replace(val, table):
            if type(val) is not unicode:
                val = unicode(val, 'utf-8')

            for lang, safe in table:
                if type(lang) is not unicode:
                    lang = unicode(lang, 'utf-8')
                val, n = re.subn(r'\s+(?=%s)[^\d\s]+' % lang, ' ' + safe, val.lower())  # re.UNICODE, re.LOCALE, re.IGNORECASE
                if n:
                    return val, n

            return val, 0

        # re.findall(r'(?=py)[^\s]+', 'python , 2013') -> ['python']
        value, n = replace(value, self.month_table)
        if not n and type(self.patch_table) is dict:
            value, n = replace(value, self.patch_table.iteritems())

        # todo: make string safe (leave only ascii)
        return value.encode('ascii', 'ignore')

    def _get(self, value):
        try:
            return parse_date(self.normalize(value)).replace(tzinfo=utc)
        except (ValueError, TypeError) as e:
            return self.default

    @staticmethod
    def default_date():
        return datetime.utcnow().replace(tzinfo=utc)


class FullUrl():
    def __init__(self):
        self.base_url = None

    def __call__(self, values):
        if not self.base_url:
            return values

        return [join(self.base_url, basename(url)) for url in values]  # urljoin

    @staticmethod
    def clean_full_domain(url):
        url = list(urlparse(url))
        url[0] = ''  # scheme
        url[1] = ''  # netloc
        return urlunparse(url)  # .geturl()

    @staticmethod
    def full_domain(url):
        """Extracts the full domain name with scheme"""
        url = urlparse(url)
        return '://'.join((url.scheme, url.netloc))


class TagItem(Item):
    name = Field()


class CategoryItem(DjangoItem):
    django_model = Category


class IndexArticleItem(Item):
    link = Field()


class ArticleItem(DjangoItem):
    django_model = Article

    categories = Field()
    tagline = Field()
    image_urls = Field()
    images = Field()
    site = Field()
    date_of = Field()
    body_text = Field()

    def __init__(self, *args, **kwargs):
        super(ArticleItem, self).__init__(*args, **kwargs)

        self["categories"] = []
        self["tagline"] = []
        self["image_urls"] = []
        self["images"] = []
        self["site"] = None
        self["date_of"] = ParseDate.default_date()
        self["body_text"] = ''
        self['headline'] = ''


class TaglineLoader(XPathItemLoader):
    pass


class CategoryLoader(XPathItemLoader):
    # TakeFirst()
    name_out = Compose(
        Join(),
        TextTool(strip=True, normalize=True, first_line=True, trim_number=settings.PARSE_CATEGORY_TRIM_SIZE)
    )

    def __init__(self, search_map, response):
        super(CategoryLoader, self).__init__(item=CategoryItem(), response=response)

        self.add_xpath('name', search_map['category'])


class ArticleLoader(XPathItemLoader):
    category_loader = CategoryLoader
    tagline_loader = TaglineLoader

    url_out = Join()
    body_text_out = Compose(Join(), TextTool(normalize=True))
    date_of_out = Compose(TakeFirst(), ParseDate(patch_table={u"мая": "May"}))
    headline_out = Compose(Join(), TextTool(normalize=True))
    #image_urls_out = FullUrl()

    def __init__(self, search, response, check_exists=False):
        self.search = search
        self.response = response
        self.check_exists = check_exists

        super(ArticleLoader, self).__init__(item=ArticleItem(), response=self.response)

    def load_item(self):
        self._configure_main_rules()
        if self.check_exists and ArticleChecker(url=self.response.url,
                                                headline=self.get_output_value('headline')).exists():
            return

        result = super(ArticleLoader, self).load_item()
        return result if result['headline'] else None

    def _configure_main_rules(self):
        self.add_value('url', self.response.url)
        for field, xpath in self.search.iteritems():
            try:
                self.add_xpath(field, xpath)
            except KeyError:
                continue

    def _load_category_item(self):
        try:
            category_loader = self.category_loader(self.search, self.response)
            category = category_loader.load_item()
            if not (category and category['name']):
                raise ValueError()
        except (KeyError, ValueError):
            pass  # -> category rule not exists - simple skip this case
        else:
            self._setup_text_processing(category)
            self.item["categories"].append(category)

    def _setup_text_processing(self, category):
        self.body_text_out.cut_substring = category['name']


class ArticleChecker():
    def __init__(self, url=None, headline=None):
        self._hashline = {}
        self.append(url, headline)

    def append(self, url, headline):
        if url and headline:
            self._hashline[Article.make_hash(url, headline)] = url  # headline

    def exists(self):
        if not self._hashline:
            raise ValueError(
                'Links was not extracted, check the correctness of the specified rules (xpath expressions)')

        return self._articles().count() > 0

    def get_fresh_urls(self):
        exists_hashline = set(article['hash'] for article in self._articles().values('hash'))

        # non-symmetric: exists hashline is subset of all hashline
        fresh_hashline = set(self._hashline).difference(exists_hashline)

        return [self._hashline[hash] for hash in fresh_hashline], exists_hashline

    def _articles(self):
        return Article.objects.filter(hash__in=self._hashline.keys())

    @classmethod
    def from_page(cls, response, search):
        obj = cls()

        strip = TextTool()
        selector = Selector(text=response.body)
        links = selector.xpath(search['link'])

        for link in links:
            url = link.xpath('@href').extract().pop()
            headline = strip(link.xpath('text()').extract().pop())
            obj.append(url, headline)

        return obj
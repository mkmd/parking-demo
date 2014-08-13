# -*- coding: utf-8 -*-

import hashlib
from slugify import slugify
from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from categories.models import CategoryBase

from .base import ArticleBase
from .parser import SiteSlice


class Category(CategoryBase):
    class Meta(CategoryBase.Meta):
        app_label = 'crawler'
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    class MPTTMeta:
        order_insertion_by = ('order', 'name')

    order = models.IntegerField(unique=True, default=0, editable=False)
    description = models.TextField(blank=True, null=True)

    @property
    def short_title(self):
        return self.name
    
    def save(self, *args, **kwargs):
        #if self.pk:
        #    self.order = F('order') + 1
        if not self.order:
            self.order = (Category.objects.count() or 0) + 1
        super(Category, self).save(*args, **kwargs)


class Article(ArticleBase):
    """
    Parsed article (see "manage.py crawl" command)
    """

    class Meta:
        app_label = 'crawler'

    site = models.ForeignKey(SiteSlice, blank=False)
    url = models.URLField(max_length=255)
    date_of = models.DateTimeField()
    categories = models.ManyToManyField('Category', blank=True)
    tagline = TaggableManager(related_name='article_tags', blank=True)
    _hash = models.CharField(max_length=255, name='hash', db_column='hash', editable=False, unique=True)
    #body_images = models.TextField(editable=False, help_text=_('Comma-separated list of images, used in body text'), blank=True)
    #enabled = models.BooleanField(default=True)

    @property
    def hash(self):
        return self.make_hash(self.url, self.headline)

    # emulating the behavior of the field: no op
    @hash.setter
    def hash(self, value):
        pass

    #http://djbook.ru/rel1.6/topics/signals.html
    def save(self, *args, **kwargs):
        super(Article, self).save(*args, **kwargs)

    @staticmethod
    def make_hash(url, headline):
        if not (url and headline):
            return

        return hashlib.md5(slugify(headline + url)).hexdigest()
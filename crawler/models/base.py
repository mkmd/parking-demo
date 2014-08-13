# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _


class ArticleBase(models.Model):
    """
    Base abstract article
    """

    class Meta:
        abstract = True
        app_label = 'crawler'

    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.headline

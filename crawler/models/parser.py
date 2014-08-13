# -*- coding: utf-8 -*-

from datetime import timedelta
import logging
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import Signal, pre_save
from django.utils.translation import ugettext as _
from interval.fields import IntervalField
from taggit.managers import TaggableManager
from jsonfield import JSONField

#from crawler.contrib.utils import modelfield
from crawler.bot import load_spider_rule_template, load_spider
from .managers import SiteSliceManager
from contrib.utils import make_shortcut

logger = logging.getLogger(__name__)


# todo: add Rule object (parse & extract content from page)
# todo: add cut rules (remove pieces from content body)

class Parser(models.Model):
    class Meta:
        app_label = 'crawler'

    # choices=[(None, None)],
    engine = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Spider module'))
    label = models.CharField(max_length=127, blank=False, null=False, verbose_name=_('Human readable name'))
    rules = JSONField(verbose_name=_('Spider rules to extract the content'), default=[])

    #download_delay

    # note: to prevent "god" anti-pattern extract field (RulesField, needs instance initialization)
    # note: try to make thin field wrapper (virtual multi-field), which aggregate logic of multiple fields

    def __unicode__(self):
        return self.label

    @property
    def engine_shortcut(self):
        # if not self.engine:
        #     self.engine = self._meta.get_field('engine').default  # modelfield(self, 'engine').default
        return make_shortcut(self.engine)

    @property
    def rules_template(self):
        try:
            return load_spider_rule_template(self.engine_shortcut)
        except (IOError, TypeError):
            return self._meta.get_field('rules').default

    def spider(self, site):
        spider = load_spider(self.engine)
        try:
            opts = {
                "name": site.label,
                "allowed_domains": site.domains_list,
                "start_urls": site.urls_list,
                "rules": self.rules
            }
            return spider(site.pk, **opts)
        except KeyError:
            # todo: & use "Improperly configured"
            logger.error(_('Spider settings for parser "%s" was defined in bad format.'), self.label)
            raise


class SiteSlice(models.Model):  # dict
    """Maintains a list of addresses, used for site-crawling process."""

    class Meta:
        app_label = 'crawler'

    objects = models.Manager()
    active = SiteSliceManager()

    enabled = models.BooleanField(default=True)
    parser = models.ForeignKey(Parser, help_text=_('Select the parser engine'))  # related_name='site',
    label = models.CharField(max_length=255, help_text=_('Human-readable name'), blank=False, null=False)
    domains = models.CharField(max_length=255, help_text=_('Allowed domains'), blank=True)
    urls = models.TextField(help_text=_('Crawling address list'), blank=False)
    rotate_time = IntervalField(format='DH', help_text=_('Rotate time interval'), default=timedelta(days=1))
    tagline = TaggableManager(blank=True, verbose_name=_("Tags"))  # %(app_label)_%(class), related_name='urlset_tags',

    def __unicode__(self):
        return self.label

    @property
    def short_summary(self):
        """Get the summary stat"""
        return "Articles count: %s, last parsed at: %s" % (self.summary.parsed_n_articles, self.summary.last_parse_time)

    @property
    def domains_list(self):
        return (self.domains and self.domains.split(',')) or []

    @property
    def urls_list(self):
        return (self.urls and self.urls.split(',')) or []

    def update_summary(self):
        pass

    # todo: use "defer" argument
    def deactivate(self):
        self.enabled = False
        self.save()

    def activate(self):
        self.enabled = True
        self.save()


class Summary(models.Model):
    """Keeps summary statistics for the parsed address list."""

    class Meta:
        app_label = 'crawler'

    site = models.OneToOneField(SiteSlice, related_name='summary')
    last_parse_time = models.DateTimeField(auto_now_add=True, auto_now=True, blank=True, null=True, verbose_name=_('Last parse time'))
    next_parse_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Next parse time'))
    parsed_n_articles = models.IntegerField(default=0, blank=True, null=False, verbose_name=_('Last parsed articles counter'))
    warns = models.IntegerField(default=0, blank=True, null=False, verbose_name=_('Last parsing warning number'))
    errors = models.IntegerField(default=0, blank=True, null=False, verbose_name=_('Last parsing errors number'))


def update_next_parse_time(summary, site):
    if not (summary.last_parse_time and site.rotate_time):
        return

    summary.next_parse_time = summary.last_parse_time + site.rotate_time

@receiver(pre_save, sender=Summary)
def summary_update_time(sender, **kwargs):
    update_next_parse_time(kwargs['instance'], kwargs['instance'].site)

@receiver(pre_save, sender=SiteSlice)
def site_update_time(sender, **kwargs):
    kwargs['instance'].summary.save()

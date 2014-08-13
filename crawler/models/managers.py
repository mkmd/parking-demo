# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import F
from django.utils import timezone


class SiteSliceManager(models.Manager):
    #def all(self):
        # datetime.today()
        # , parsed_at__gte=models.F('rotate_time') + timezone.now()
        #return super(SiteSliceManager, self).filter(enabled=True)

    def get_queryset(self):
        return super(SiteSliceManager, self).get_queryset().filter(
            enabled=True,
            summary__last_parse_time__lt=timezone.now()
        )

    # def rotated(self):  # get_queryset
    #     #return super(SiteSliceManager, self).get_queryset()\
    #     #    .filter(enabled=True, summary__parsed_at__lt=timezone.now() - F('rotate_time'))
    #     # return super(SiteSliceManager, self).get_queryset().filter(enabled=True)
    #
    #     sql = """
    #         SELECT s.* FROM "crawler_siteslice" as s
    #             INNER JOIN "crawler_summary" as sum ON ( s."id" = sum."site_id" )
    #         WHERE s.enabled = 1
    #             and (sum."parsed_at" < (datetime(strftime("%s", "now") - s."rotate_time" / 10000000, "unixepoch")))
    #     """
    #
    #     return self.raw(sql)

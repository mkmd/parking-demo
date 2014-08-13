# Scrapy settings for blogbot project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'blogspot'

SPIDER_MODULES = ['blogspot.spiders']
NEWSPIDER_MODULE = 'blogspot.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'blogbot (+http://www.yourdomain.com)'

# note: use pipelines ("middleware"-stereotype) to transform the scraped items
ITEM_PIPELINES = {
    'blogspot.pipelines.StoreArticle': 20,
    'scrapy.contrib.pipeline.images.ImagesPipeline': 10,
}

import sys
import os

if not 'DJANGO_SETTINGS_MODULE' in os.environ:
    # Append path to crawler path: this project depends on it.

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'parking.settings'

from django.conf import settings

IMAGES_STORE = settings.MEDIA_ROOT

DOWNLOADER_DEBUG = False
CONCURRENT_REQUESTS = 5
DOWNLOAD_TIMEOUT = 300
DOWNLOAD_DELAY = 0.25
RANDOMIZE_DOWNLOAD_DELAY = True
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 ' \
             'Safari/537.36'  # Scrapy/VERSION (+http://scrapy.org)
#MEMUSAGE_ENABLED

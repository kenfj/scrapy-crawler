# -*- coding: utf-8 -*-
import os
import json
import html
import random
import urllib.parse
import urllib.request

from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from tqdm import tqdm
from appstore_crawler.spiders.app_item import item_generator
from appstore_crawler.spiders.shoebox_item import shoebox_generator


app_store_home = 'https://apps.apple.com/us/genre/ios/id36'


def crawl_rules(category):
    # Extract links matching '/genre/ios-***' (but not matching 'letter=')
    # and follow links from them (since no callback means follow=True by default).

    allow_urls = (f"/genre/ios-{category}")

    # please use (1) or (2)

    # (1) this is to check only popular apps on category top page for testing
    genre_links = LinkExtractor(allow=allow_urls, deny=('letter='))
    # (2) this is to check category top page plus all sub pages for each letter
    # genre_links = LinkExtractor(allow=allow_urls)

    # Extract links matching '/app/' and parse them with the spider's method parse_item
    # also there is a link to Apple Store App in footer which should be skipped
    app_links = LinkExtractor(allow=('/app/',), deny=('ct=footer',))

    return (
        Rule(genre_links),
        Rule(app_links, callback='parse_item', follow=False),
    )


# https://doc.scrapy.org/en/latest/topics/spiders.html#crawlspider-example
class AppstoreSpider(CrawlSpider):
    name = 'appstore'
    allowed_domains = ['apps.apple.com']
    start_urls = [app_store_home]
    custom_settings = {
        'LOG_FILE': 'logs/scrapy_%d.log' % random.randrange(10000, 100000),
    }
    retry_xpath = '//script[@type="application/ld+json"]/text()'

    # category is passed from command line argument
    # scrapy crawl appstore -a category=productivity
    def __init__(self, category='', *args, **kwargs):
        self.category = category
        self.logger.info('crawl category: %s', category)

        # if no category, crawl all categories
        self.rules = crawl_rules(category)

        super().__init__(*args, **kwargs)

    def parse_item(self, response):
        self.logger.info('URL: %s', response.url)

        self.pbar.update()
        yield from shoebox_generator(response)
        yield from item_generator(response, self.category, self.logger)

    # show progress bar
    # https://stackoverflow.com/questions/12394184
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AppstoreSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.request_scheduled,
                                signals.request_scheduled)
        crawler.signals.connect(spider.item_scraped, signals.item_scraped)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        # https://stackoverflow.com/questions/28169756
        request_size = len(self.crawler.engine.slot.scheduler)
        # if 1st run, initial request_size is 0. if resumed, it is remaining requests.
        self.max_request_size = request_size

        self.pbar = tqdm(total=request_size)  # initialize progress bar
        self.pbar.clear()
        self.pbar.write('Opening {} spider'.format(spider.name))

    def request_scheduled(self, spider):
        # if 1st run, this is called. if resumed, this is not called.
        self._update_max_request_size()

    def item_scraped(self, spider):
        request_size = len(self.crawler.engine.slot.scheduler)

        # if initial scrape, recreate pbar with new total.
        if request_size >= self.max_request_size:
            self.logger.info('request size: %s', request_size)
            self._update_max_request_size()
            self.pbar.close()  # close progress bar
            self.pbar = tqdm(total=request_size)  # initialize progress bar

        self.pbar.update()  # update progress bar by 1

    def spider_closed(self, spider):
        self.logger.info('scheduler size spider_closed: %s',
                         len(self.crawler.engine.slot.scheduler))
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()  # close progress bar

    def _update_max_request_size(self):
        self.max_request_size = max(self.max_request_size, len(
            self.crawler.engine.slot.scheduler))

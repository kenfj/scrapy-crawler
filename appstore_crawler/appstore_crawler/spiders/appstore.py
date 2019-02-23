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
from appstore_crawler.items import AppstoreCrawlerItem
from tqdm import tqdm


app_store_home = 'https://itunes.apple.com/us/genre/ios/id36?mt=8'


def crawl_rules(category):
    return (
        # Extract links matching '/genre/ios-***' (but not matching 'letter=')
        # and follow links from them (since no callback means follow=True by default).

        # please use (1) or (2)

        # (1) this is to check only popular apps on category top page for testing
        Rule(LinkExtractor(allow=('/genre/ios-%s' % category,), deny=('letter=',))),

        # (2) this is to check category top page plus all sub pages for each letter
        # Rule(LinkExtractor(allow=('/genre/ios-%s' % category,))),

        # Extract links matching '/app/' and parse them with the spider's method parse_item
        # also there is a link to Apple Store App in footer which should be skipped
        Rule(LinkExtractor(allow=('/app/',), deny=('ct=footer',)), callback='parse_item', follow=False),
    )


# https://doc.scrapy.org/en/latest/topics/spiders.html#crawlspider-example
class AppstoreSpider(CrawlSpider):
    name = 'appstore'
    allowed_domains = ['itunes.apple.com']
    start_urls = [app_store_home]
    custom_settings = {
        'LOG_FILE': 'logs/scrapy_%d.log' % random.randrange(10000, 100000),
    }

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

        text_ld = response.xpath('//script[@type="application/ld+json"]/text()')
        json_ld = json.loads(text_ld.extract_first())

        text_sb = response.xpath('//script[@id="shoebox-ember-data-store"]/text()')
        shoebox = json.loads(text_sb.extract_first())
        attributes = shoebox['data']['attributes']

        item = self._create_item(json_ld, attributes)

        # sometimes the popular app list mixes different category
        # if the app is not in the category, skip and continue
        # https://stackoverflow.com/questions/5040110
        if self.category and self.category != self._snake_case(item['category']):
            self.logger.info('SKIPPING... %s %s %s', item['category'], item["id"], item['name'])
            return

        # need LANG=en_US.utf8 in /etc/default/locale (c.f. Dockerfile)
        self.logger.info('SAVING... %s %s %s', item['category'], item["id"], item['name'])

        img_src = response.xpath('//div[contains(@class, "product-hero__media")]//img/@src').extract_first()
        icon_file = self._icon_file(item['category'], item['id'])

        if not os.path.exists(icon_file):
            self.logger.info(' %s', icon_file)
            self._save_icon(img_src, icon_file)

        return item

    @staticmethod
    def _create_item(json_ld, attributes):
        item = AppstoreCrawlerItem()

        item['id'] = attributes['metricsBase']['pageId']
        item['category'] = json_ld['applicationCategory']
        item['name'] = json_ld['name']
        item['subtitle'] = attributes.get('subtitle', '')
        item['url'] = attributes['url']
        item['description'] = json_ld['description']
        item['date_published'] = json_ld['datePublished']
        item['rating_value'] = attributes['userRating']['value']
        item['rating_count'] = attributes['userRating']['ratingCount']
        item['rating_count_list'] = attributes['userRating']['ratingCountList']

        if attributes.get('chartPositionForStore', {}).get('appStore'):
            item['chart_genre_name'] = attributes['chartPositionForStore']['appStore']['genreName']
            item['chart_position'] = attributes['chartPositionForStore']['appStore']['position']

        item['price_category'] = json_ld['offers'].get('category', '')
        item['price'] = json_ld['offers']['price']
        item['price_currency'] = json_ld['offers']['priceCurrency']
        item['has_in_app_purchases'] = attributes.get('hasInAppPurchases', "false")
        item['author_url'] = json_ld['author']['url']
        item['author_name'] = json_ld['author']['name']
        item['website_url'] = attributes['softwareInfo']['websiteUrl']

        # fix &amp; to &
        item['name'] = html.unescape(item['name'])
        item['category'] = html.unescape(item['category'])

        # fix %xx to readable string
        item['url'] = urllib.parse.unquote(item['url'])

        return item

    @staticmethod
    def _icon_file(category, id_):
        category = AppstoreSpider._snake_case(category)
        directory = 'icondata/%s' % category

        if not os.path.exists(directory):
            os.makedirs(directory)

        return '%s/%s.jpg' % (directory, id_)

    @staticmethod
    def _snake_case(words):
        # adjust to url (Food & Drink -> food-drink)
        return words.replace(' & ', '-').replace(' ', '-').lower()

    @staticmethod
    def _save_icon(img_src, icon_file):
        try:
            urllib.request.urlretrieve(img_src, icon_file)
        except Exception:
            # retry in case of urllib.error.URLError
            # <EOF occurred in violation of protocol (_ssl.c:645)>
            urllib.request.urlretrieve(img_src, icon_file)

    # show progress bar
    # https://stackoverflow.com/questions/12394184
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AppstoreSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.request_scheduled, signals.request_scheduled)
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
        self.logger.info('scheduler size spider_closed: %s', len(self.crawler.engine.slot.scheduler))
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()  # close progress bar

    def _update_max_request_size(self):
        self.max_request_size = max(self.max_request_size, len(self.crawler.engine.slot.scheduler))

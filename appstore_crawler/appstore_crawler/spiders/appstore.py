# -*- coding: utf-8 -*-
import scrapy


class AppstoreSpider(scrapy.Spider):
    name = 'appstore'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    def parse(self, response):
        pass

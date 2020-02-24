# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AppstoreCrawlerItem(scrapy.Item):
    id = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    subtitle = scrapy.Field()
    url = scrapy.Field()
    img_src = scrapy.Field()
    description = scrapy.Field()
    date_published = scrapy.Field()

    rating_value = scrapy.Field()
    rating_count = scrapy.Field()
    rating_ratio = scrapy.Field()

    price_category = scrapy.Field()
    price = scrapy.Field()
    price_currency = scrapy.Field()
    has_in_app_purchases = scrapy.Field()

    author_name = scrapy.Field()
    author_url = scrapy.Field()


class FastbootShoeboxItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    subtitle = scrapy.Field()
    artist_name = scrapy.Field()
    url = scrapy.Field()

    rating_value = scrapy.Field()
    rating_count = scrapy.Field()
    rating_count_list = scrapy.Field()

    chart_name = scrapy.Field()
    chart_position = scrapy.Field()
    chart_genre_name = scrapy.Field()
    chart_genre_id = scrapy.Field()

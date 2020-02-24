# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import urllib

from scrapy.exporters import CsvItemExporter
from appstore_crawler.items import AppstoreCrawlerItem, FastbootShoeboxItem
from appstore_crawler.spiders.appstore import AppstoreSpider
from appstore_crawler.spiders.appstore_util import snake_case

# https://stackoverflow.com/questions/32743469/scrapy-python-multiple-item-classes-in-one-pipeline
# https://qiita.com/bakeratta/items/6fe9030ad838a2a71aa5
# https://www.reddit.com/r/scrapy/comments/87z467/how_do_i_save_scraped_items_to_multiple_jl_files/


class AppstoreCrawlerPipeline(object):
    def open_spider(self, spider):
        # https://stackoverflow.com/questions/27513707/using-arguments-in-scrapy-pipeline-on-init
        filename = f"csvdata/{spider.category or 'all'}.csv"
        self.csv_file = open(filename, "ab")
        self.exporter = CsvItemExporter(self.csv_file)
        self.exporter.fields_to_export = [
            "id",
            "category",
            "name",
            "subtitle",
            "url",
            "date_published",
            "rating_value",
            "rating_count",
            "rating_ratio",
            "price_category",
            "price",
            "price_currency",
            "has_in_app_purchases",
            "author_name",
            "author_url",
            "description",
        ]

    def process_item(self, item, spider):
        if isinstance(item, AppstoreCrawlerItem):
            self.exporter.export_item(item)
            self.save_icon(item, spider)

        return item

    def close_spider(self, spider):
        self.csv_file.close()

    def save_icon(self, item, spider):
        icon_file = self._icon_file(item)

        if not os.path.exists(icon_file):
            spider.logger.info(' %s', icon_file)
            self._urlretrieve_icon(item["img_src"], icon_file)

    def _icon_file(self, item):
        _, img_ext = os.path.splitext(item["img_src"])

        category = snake_case(item["category"])
        directory = f"icondata/{category}"

        if not os.path.exists(directory):
            os.makedirs(directory)

        return f"{directory}/{item['id']}{img_ext}"

    def _urlretrieve_icon(self, img_src, icon_file):
        try:
            urllib.request.urlretrieve(img_src, icon_file)
        except urllib.error.URLError:
            # retry in case of urllib.error.URLError
            # <EOF occurred in violation of protocol (_ssl.c:645)>
            urllib.request.urlretrieve(img_src, icon_file)


class FastbootShoeboxPipeline(object):
    def open_spider(self, spider):
        filename = f"csvdata/{spider.category or 'all'}_sb.csv"
        self.csv_file = open(filename, "ab")
        self.exporter = CsvItemExporter(self.csv_file)
        self.exporter.fields_to_export = [
            "id",
            "name",
            "subtitle",
            "url",
            "rating_value",
            "rating_count",
            "rating_count_list",
            "artist_name",
            "chart_name",
            "chart_position",
            "chart_genre_name",
            "chart_genre_id",
        ]

    def process_item(self, item, spider):
        if isinstance(item, FastbootShoeboxItem):
            self.exporter.export_item(item)

        return item

    def close_spider(self, spider):
        self.csv_file.close()

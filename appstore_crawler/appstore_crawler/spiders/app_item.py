

import re
import json
import html
import urllib

from datetime import datetime
from dateutil import parser
from appstore_crawler.items import AppstoreCrawlerItem
from appstore_crawler.spiders.appstore_util import snake_case


def item_generator(response, category, logger):
    item = _create_item(response, logger)

    # sometimes the popular app list mixes different category
    # if the app is not in the category, skip and continue
    # https://stackoverflow.com/questions/5040110
    if category and category != snake_case(item['category']):
        logger.info('SKIPPING... %s %s %s',
                    item['category'], item["id"], item['name'])
        return

    # need LANG=en_US.utf8 in /etc/default/locale (c.f. Dockerfile)
    logger.info('SAVING... %s %s %s',
                item['category'], item["id"], item['name'])

    yield item


def _parse_date(text, logger):
    try:
        datetime_published = parser.parse(text)
        date_published = datetime_published.date().isoformat()
    except parser.ParserError as err:
        try:
            fmt = "%Y年%m月%d日"
            datetime_published = datetime.strptime(text, fmt)
            date_published = datetime_published.date().isoformat()
        except ValueError as err:
            # for example id1085652055, Unknown string format: 11 Nis 2016
            logger.warning(err)
            date_published = text

    return date_published


def _create_item(response, logger):
    ld_xpath = '//script[@type="application/ld+json"]/text()'
    ld_json = json.loads(response.xpath(ld_xpath).get())

    id_ = re.findall("id\d+", response.url)[0][2:]
    subtitle = response.css("h2.app-header__subtitle::text").get()

    date_published = _parse_date(ld_json['datePublished'], logger)

    bars = response.css("div.we-star-bar-graph__bar__foreground-bar")
    styles = bars.xpath('@style').getall()
    rating_ratio = "-".join([re.findall("\d+", style)[0]
                             for style in styles])

    in_app_purchase_css = "li.app-header__list__item--in-app-purchase::text"
    in_app_purchase = response.css(in_app_purchase_css).get(default="No")

    img_src_xpath = '//div[contains(@class, "product-hero__media")]//img/@src'
    img_src = response.xpath(img_src_xpath).get()

    item = AppstoreCrawlerItem()

    item['id'] = id_
    item['category'] = ld_json['applicationCategory']
    item['name'] = ld_json['name']
    item['subtitle'] = subtitle
    item['url'] = response.url
    item['description'] = re.sub("[\r\n]+", " ", ld_json['description'])
    item['date_published'] = date_published

    item['rating_value'] = ld_json['aggregateRating']['ratingValue']
    item['rating_count'] = ld_json['aggregateRating']['reviewCount']
    item['rating_ratio'] = rating_ratio

    item['price_category'] = ld_json['offers'].get('category', '')
    item['price'] = ld_json['offers']['price']
    item['price_currency'] = ld_json['offers']['priceCurrency']
    item['has_in_app_purchases'] = in_app_purchase

    item['author_name'] = ld_json['author']['name']
    item['author_url'] = ld_json['author']['url']

    item['img_src'] = img_src

    # fix &amp; to &
    item['name'] = html.unescape(item['name'])
    item['category'] = html.unescape(item['category'])

    # fix %xx to readable string
    item['url'] = urllib.parse.unquote(item['url'])

    return item

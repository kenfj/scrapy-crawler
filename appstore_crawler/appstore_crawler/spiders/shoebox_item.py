

import json

from appstore_crawler.items import FastbootShoeboxItem


def shoebox_generator(response):
    sb_xpath = '//script[@id="shoebox-ember-data-store"]/text()'
    sb_text = response.xpath(sb_xpath).get()

    # sb_text can be None
    if sb_text:
        sb_json = json.loads(sb_text)

        for elm in sb_json['data']:
            yield _create_shoebox_item(elm)


def _create_shoebox_item(elm):
    att = elm["attributes"]
    rating = elm["attributes"]["userRating"]
    default = {"appStore": {
        "chart": None, "position": None, "genreName": None, "genre": None}
    }
    chart = elm["attributes"]\
        .get("chartPositions", default)\
        .get("appStore", default["appStore"])
    att2 = elm["relationships"]["platforms"]["data"][0]["attributes"]

    item = FastbootShoeboxItem()

    item["id"] = elm["id"]
    item["name"] = att["name"]
    item["subtitle"] = att2.get("subtitle")
    item["url"] = att["url"]
    item["rating_value"] = rating["value"]
    item["rating_count"] = rating["ratingCount"]
    item["rating_count_list"] = rating["ratingCountList"]
    item["artist_name"] = att["artistName"]
    item["chart_name"] = chart["chart"]
    item["chart_position"] = chart["position"]
    item["chart_genre_name"] = chart["genreName"]
    item["chart_genre_id"] = chart["genre"]

    return item

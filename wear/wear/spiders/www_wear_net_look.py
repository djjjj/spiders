# -*- coding: utf-8 -*-
import scrapy
import re

from pyquery import PyQuery


class WwwWearNetLookSpider(scrapy.Spider):
    name = 'www_wear_net_look'
    allowed_domains = []
    start_urls = ['http://https://wear.net/bethanymarieco/12566671//']

    re_height_patten = re.compile("\d'\d""")

    def parse(self, response):
        html = response.text
        doc = PyQuery(html)('#content_main')
        self._parse_html(doc)

    def _parse_html(self, doc):
        look = dict()
        look['imgUrl'] = \
            "http:" + doc("#coordinate_img").children("p.img").children("img").attr("src")
        height = re.search("")doc('#coordinate_info')('.model_info').text()
        look['modelHeight'] = ""
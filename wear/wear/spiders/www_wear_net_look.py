# -*- coding: utf-8 -*-
import time
import scrapy
import re

from pyquery import PyQuery
from scrapy import Request

from ..redis_utils import look_ids_queue


class WwwWearNetLookSpider(scrapy.Spider):
    name = 'www_wear_net_look'
    allowed_domains = []
    start_urls = ['https://wear.net/bethanymarieco/12566671/']

    re_height_patten = re.compile("\d'\d\"")
    re_like_count_patten = re.compile('over"><span>([0-9]+)')
    re_user_ids_patten = re.compile('name"><a href="/(.*?)/"')

    domain = "wear.net"
    url_patten = 'https://' + domain + '/%s/'

    def start_requests(self):
        look_id = look_ids_queue.spop()
        while look_id:
            look_id = look_id.decode('utf8')
            url = self.url_patten % look_id
            yield Request(url, meta={'look_id': look_id}, callback=self.parse)
            look_id = look_ids_queue.spop()
            time.sleep(0.1)

    def parse(self, response):
        html = response.text
        look_id = response.meta['look_id']
        doc = PyQuery(html)('#content_main')
        look = self._parse_html(doc)
        look['lookId'] = look_id
        yield look

        like_count = int(self.re_like_count_patten.search(html).group(1))
        if like_count != 0:
            url = self.url_patten % (look_id + "/like")
            yield Request(url, meta={"look_id": look_id}, callback=self.parse_like)
            like_count = like_count // 40 + 1
            for i in range(2, like_count + 1):
                new_url = url + '?pageno=%d' % i
                yield Request(new_url, meta={"look_id": look_id}, callback=self.parse_like)

    def parse_like(self, response):
        look_id = response.meta['look_id']
        html = response.text
        users = self.re_user_ids_patten.findall(html)
        yield {'lookId': look_id, 'likeUsers': users}

    def _parse_html(self, doc):
        look = dict()
        look['imgUrl'] = \
            "http:" + doc("#coordinate_img").children("p.img").children("img").attr("src")
        height = \
            self.re_height_patten.search(doc('#coordinate_info')('.model_info').text())
        if height:
            look['modelHeight'] = height.group(0)
        items = doc("#item").children("ul").children()
        item_list = []
        for i in items:
            i = PyQuery(i)
            item = dict()
            item['imgUrl'] = "http:" + i(".sub")('p.img')('img').attr("src")
            item['brand'] = i('.main')('.brand').text()
            item['category'] = i('.main')('.txt')("a").text()
            item_list.append(item)
        if item_list:
            look['items'] = item_list
        return look

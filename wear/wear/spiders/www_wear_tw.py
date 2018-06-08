# -*- coding: utf-8 -*-
import re
import time
import scrapy

from scrapy import Request
from pyquery import PyQuery

from ..redis_utils import user_queue, look_ids_queue


class WwwWearTwSpider(scrapy.Spider):
    name = 'www_wear_tw'
    allowed_domains = []

    domain = 'wear.tw'
    url_patten = 'https://' + domain + '/%s/'

    re_user_id_patten = re.compile("/([^/]+)/$")
    re_user_ids_patten = re.compile('h3 class="name"><a href="/(.*?)/')
    re_follow_patten = re.compile("follow/.*?([0-9]+)<span")
    re_follower_patten = re.compile("follower/.*?([0-9]+)<span")

    re_look_ids_patten = re.compile('data-snapId="([0-9]+)')
    re_look_count_patten = re.compile('class="current.*>([0-9]+)')

    def start_requests(self):
        user_id = user_queue.spop()
        while user_id:
            user_id = user_id.decode('utf8')
            url = self.url_patten % user_id
            yield Request(url, callback=self.parse)
            user_id = user_queue.spop()
            time.sleep(0.3)

    def parse_look(self, response):
        user_id = response.meta['user_id']
        html = response.text
        look_ids = [user_id+"/"+_ for _ in self.re_look_ids_patten.findall(html)]
        if look_ids:
            look_ids_queue.sadd(*look_ids)

    def parse_follow(self, response):
        user_ids = self.re_user_ids_patten.findall(response.text)
        if user_ids:
            user_queue.sadd(*user_ids)
        for user_id in user_ids:
            url = self.url_patten % user_id.lower()
            yield Request(url, callback=self.parse)

    def parse(self, response):
        url = response.url
        user_id = self.re_user_id_patten.search(url).group(1)
        html = response.text
        count = int(self.re_look_count_patten.search(html).group(1))
        look_ids = [user_id+"/"+_ for _ in self.re_look_ids_patten.findall(html)]
        if look_ids:
            look_ids_queue.sadd(*look_ids)
        page_count = count // 56 + 1
        if page_count > 250:
            page_count = 250
        url = self.url_patten % user_id
        for i in range(2, page_count + 1):
            new_url = url + '?pageno=%i' % i
            yield Request(new_url, meta={'user_id': user_id}, callback=self.parse_look)

        doc = PyQuery(html)('#gbl_main')
        user = self._parse_html(doc)
        user['userId'] = user_id
        yield user

        # follower_count = int(
        #     self.re_follower_patten.search(html).group(1)) // 40 + 1
        # if follower_count > 250:
        #     follower_count = 250
        # follow_count = int(
        #     self.re_follow_patten.search(html).group(1)) // 40 + 1
        # if follow_count > 250:
        #     follow_count = 250
        # followers_url = self.url_patten % user_id.lower() + 'follower/'
        # follows_url = self.url_patten % user_id.lower() + 'follow/'
        # yield Request(followers_url, callback=self.parse_follow)
        # yield Request(follows_url, callback=self.parse_follow)
        # for i in range(2, follower_count + 1):
        #     new_url = followers_url + '?pageno=%i' % i
        #     yield Request(new_url, callback=self.parse_follow)
        # for i in range(2, follow_count + 1):
        #     new_url = follows_url + '?pageno=%i' % i
        #     yield Request(new_url, callback=self.parse_follow)

    def _parse_html(self, doc):
        user = dict()
        header = doc('#user_header')
        user['name'] = header.children('#user_sub').children('.image').children('.img').children('img').attr('alt')
        info = header('ul.info').children()
        for child in info[1:]:
            text = PyQuery(child).text()
            if text.endswith('cm'):
                user['height'] = text
            elif text in {'MEN', 'WOMEN', 'KIDS'}:
                user['sex'] = text
            elif text.endswith(u'嵗'):
                user['age'] = text
            elif u'髮' in text:
                user['hairstyle'] = text
            else:
                user['location'] = text
        brands = [_.text() for _ in header('.favorite')('ul').items('li')]
        if brands:
            user['brandLike'] = '|'.join(brands)
        use = [_.text() for _ in doc('#gbl_related_link')('ul').items('li')]
        if use:
            user['brandUse'] = '|'.join(use)
        return user

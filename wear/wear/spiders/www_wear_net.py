# -*- coding: utf-8 -*-
from pyquery import PyQuery

from .www_wear_tw import WwwWearTwSpider

domain = "wear.net"


class WwwWearNetSpider(WwwWearTwSpider):

    name = 'www_wear_net'

    def _parse_html(self, html):
        user = dict()
        doc = PyQuery(html)('#gbl_main')
        header = doc('#user_header')
        user['name'] = header.children('#user_sub').children('.image').children('.img').children('img').attr('alt')
        info = header('ul.info').children()
        for child in info[1:]:
            text = PyQuery(child).text()
            if text.endswith('cm'):
                user['height'] = text
            elif text in {'MEN', 'WOMEN', 'KIDS'}:
                user['sex'] = text
            elif text.endswith(u'Age'):
                user['age'] = text
            elif u'hair' in text:
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

# -*- coding: utf-8 -*-
from .www_wear_net_look import WwwWearNetLookSpider


class WwwWearTwLookSpider(WwwWearNetLookSpider):
    name = 'www_wear_tw_look'
    allowed_domains = []

    domain = "wear.tw"
    url_patten = 'https://' + domain + '/%s/'

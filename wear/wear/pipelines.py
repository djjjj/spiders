# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


data_dir = "/home/djj/data/wear/"
user_info_data = data_dir + "user_info.json"
user_info_fp = open(user_info_data, 'a')

look_info_data = data_dir + "look_info.json"
look_info_fp = open(look_info_data, 'a')


class WearPipeline(object):

    def process_item(self, item, spider):
        if spider.name in {}:
            user_info_fp.write("%s\n" % json.dumps(item))

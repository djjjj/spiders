# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import requests

from random import Random
from scrapy import signals

from .redis_utils import user_queue


r = Random()


class WearSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WearDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):

    host = "http://localhost:14001"
    get_api = host + "/"
    feedback_api = host + "/feedback"
    delete_api = host + "/delete"

    def __get_a_proxy(self):
        p = 1 #r.choice([1, 0])
        rsp = requests.get(self.get_api, params={"count": 1, "protocol": p})
        proxy_list = json.loads(rsp.text)
        for _ in proxy_list:
            _.append(p)
        return proxy_list

    def __feedback_a_proxy(self, protocol, ip, port, feedback):
        requests.get(
            self.feedback_api,
            params={"ip": ip, "port": port, "protocol": protocol, "feedback": feedback}
        )

    def process_request(self, request, spider):
        proxy = self.__get_a_proxy()
        if proxy:
            ip = "http%s://%s:%d" % ("" if proxy[0][3] == 0 else "s", proxy[0][0], proxy[0][1])
            request.meta["proxy"] = ip
            request.meta["proxy_info"] = proxy[0]

    def process_response(self, request, response, spider):
        status_code = response.status
        proxy_info = request.meta["proxy_info"]
        if status_code != 200:
            self.__feedback_a_proxy(proxy_info[3], proxy_info[0], proxy_info[1], "bad")
            user_queue.sadd(request.meta["user_id"])
        else:
            self.__feedback_a_proxy(proxy_info[3], proxy_info[0], proxy_info[1], "good")
        return response


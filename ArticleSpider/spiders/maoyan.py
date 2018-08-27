# _*_ encoding:utf-8 _*_

import scrapy

from scrapy.http import Request
from urllib import parse


class MaoyanSipder(scrapy.Spider):
    name = "maoyan"
    allowed_domains = []
    start_urls = ["http://maoyan.com/board/4"]

    def parse(self, response):
        pass


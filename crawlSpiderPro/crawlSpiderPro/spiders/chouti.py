# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ChoutiSpider(CrawlSpider):
    name = 'chouti'
    # allowed_domains = ['dig.chouti.com']
    start_urls = ['https://dig.chouti.com/']

    # 实例化了一个连接提取器对象
    link = LinkExtractor(allow=r'/all/hot/recent/\d+')
    rules = (
        # 实例化一个规则解析器对象
        Rule(link, callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        print(response)

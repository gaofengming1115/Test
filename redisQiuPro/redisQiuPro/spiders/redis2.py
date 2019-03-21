# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from redisQiuPro.items import RedisqiuproItem


class Redis2Spider(RedisCrawlSpider):
    name = 'redis2'
    # allowed_domains = ['www.qiushibaike.com']
    # start_urls = ['http://www.qiushibaike.com/']
    redis_key = 'qiubaispider'
    link = LinkExtractor(allow=r'/imgrank/page/\d+')
    rules = (
        Rule(link, callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        div_list = response.xpath('//*[@id="content-left"]/div')
        for div in div_list:
            img_url = div.xpath('./div[@class="thumb"]/a/img/@src').extract_first()
            item = RedisqiuproItem()
            item['img_url'] = img_url
            yield item

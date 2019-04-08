# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from wangyiPro.items import WangyiproItem
from scrapy_redis.spiders import RedisSpider


class WangyiSpider(RedisSpider):
    name = 'wangyi'
    # allowed_domains = ['www.xx.com']
    # start_urls = ['https://news.163.com/']
    redis_key = 'wangyi'

    def __init__(self):
        # 实例化一个浏览器对象(实例化一次)
        self.bro = webdriver.Chrome(executable_path='E:\soft\python\soft\chromedriver_win32\chromedriver.exe')

    def closed(self, spider):
        print('爬虫结束')
        self.bro.quit()

    def parse(self, response):
        lis = response.xpath('//div[@class="ns_area list"]/ul/li')
        indexs = [3, 4, 6, 7]
        li_list = []  # 存储的就是国内国际军事航空对应的标签对象
        for index in indexs:
            li_list.append(lis[index])
        # 获取四个板块中的链接，文字
        for li in li_list:
            url = li.xpath('./a/@href').extract_first()
            title = li.xpath('./a/text()').extract_first()
            # print(url+':'+title)
            yield scrapy.Request(url=url, callback=self.parseSecond, meta={'title': title})

    def parseSecond(self, response):
        div_list = response.xpath('//div[@class="data_row news_article clearfix "]')
        print(len(div_list))
        for div in div_list:
            head = div.xpath('.//div[@class="news_title"]/h3/a/text()').extract_first()
            url = div.xpath('.//div[@class="news_title"]/h3/a/@href').extract_first()
            imgUrl = div.xpath('./a/img/@src').extract_first()
            tag = div.xpath('.//div[@class="news_tag"]//text()').extract()
            tags = []
            for t in tag:
                t = t.strip(' \n \t')
                tags.append(t)
            tag = "".join(tags)
            title = response.meta['title']
            item = WangyiproItem()
            item['head'] = head
            item['url'] = url
            item['imgUrl'] = imgUrl
            item['tag'] = tag
            item['title'] = title

            yield scrapy.Request(url=url, callback=self.getContent, meta={'item': item})

    def getContent(self, response):
        # 获取传递过来的item
        item = response.meta['item']

        # 解析当前页面中存储的新闻数据
        content_list = response.xpath('//div[@class="post_text"]/p/text()').extract()
        content = "".join(content_list)
        item['content'] = content

        yield item

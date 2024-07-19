# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import ArticleItem

class PlaywrightDocSpider(CrawlSpider):
    """爬取playwright doc （用作测试）"""
    name = "playwright_doc"
    # rules = (Rule(LinkExtractor(allow=('.*', )), callback='parse_item', follow=True),)
    def start_requests(self):
        print("==================start_requests")
        urls = [
            'https://playwright.dev/python/docs/release-notes#new-apis-3',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # self.state['items_count'] = self.state.get('items_count', 0) + 1
        # print("state:count %s" % self.state.get('items_count'))
        self.logger.info('parse %s', response.url)
        
        # page = response.url.split("/")[-2]
        # filename = f'quotes-{page}.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log(f'Saved file {filename}')
        # print("url", response.url)
        # print("TEXT:", response.text)
        # for h1 in response.xpath('//h1').getall():
        #     # yield MyItem(title=h3)
        #     print(h1)
        link_ext = LinkExtractor(unique=True)
        # links = link_ext.extract_links(response)
        for link in link_ext.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_article)
        # for href in response.xpath('//a/@href').getall():
        #     yield scrapy.Request(response.urljoin(href), self.parse)
        
    def parse_article(self, response):
        # detail = response.xpath('//div[@class="article-wrap"]')
        item = ArticleItem()
        if response.xpath('//h1/text()'):
            item['title'] = "TITLE:"+ response.xpath('//h1/text()')[0].extract()
        item['link'] = response.url
        # item['posttime'] = detail.xpath(
        #     'div[@class="article-author"]/span[@class="article-time"]/text()')[0].extract()
        # print(item['title'],item['link'],item['posttime'])
        yield item
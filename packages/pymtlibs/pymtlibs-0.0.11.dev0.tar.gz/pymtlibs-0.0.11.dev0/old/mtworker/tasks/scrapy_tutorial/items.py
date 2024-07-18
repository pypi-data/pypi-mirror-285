import scrapy
from scrapy.item import Item, Field
# from scrapy.contrib.djangoitem import DjangoItem
# from scrapy_djangoitem import DjangoItem
# from .. import models

class ArticleItem(Item):
    # 爬虫名称
    crawl_name=Field()
    # 爬取网址
    crawl_url= Field()
    # 爬取日期
    crawl_at= Field()
    title=Field(max_length=64, null=False, blank=False, default=None, verbose_name = "标题")
    subtitle=Field(max_length=256, null=False, blank=False, default="", verbose_name = "副标题")
    sumary= Field(max_length=64, null=False, blank=False, default="", verbose_name = "咱要")
    link=Field(verbose_name="网址")
    html_content = Field(null=False, blank=False, default="", verbose_name = "基于html标签的正文")
    text_content = Field(null=False, blank=False, default="", verbose_name = "文本")
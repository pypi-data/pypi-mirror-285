import os,time
from pathlib import Path
from datetime import datetime
import traceback
from celery import Celery
from kombu import Queue
import time
import random
from scrapy.crawler import CrawlerProcess
from .scrapy_tutorial.spiders.playwright_doc import  PlaywrightDocSpider
from .scrapy_tutorial.spiders.quotes_spider import QuotesSpider
from celery import shared_task,chord, group, signature, uuid
from celery.signals import (
    after_setup_task_logger,
    task_success,
    task_prerun,
    task_postrun,
    celeryd_after_setup,
    celeryd_init,
)
from celery import shared_task
from .scrapy_tutorial import spiders as allSpiders

@shared_task(bind=True, name="tasks.run_spider")
def run_spider(*args, **kwargs):
    """通过celery worker 来执行爬网"""
    print("scrapy 启动",flush=True)
    item_cb_url = kwargs.get("item_cb_url")
    spider_name = kwargs.get("spider_name")
    if not spider_name:
        print("缺少参数： spider_name")
    print(f'====================================================================')
    print(f"spidername: {spider_name}, item post to : {item_cb_url}")
    print(f'=============================')
    if not item_cb_url:
        print("缺少参数：item_cb_url")
        return
    logfile = "logs/mtscrapy_log.log"
    try:
        Path(logfile).parents[0].mkdir(parents=True, exist_ok=True)
        process=CrawlerProcess(settings={
                    # "FEEDS": {
                    #     "items.json": {"format": "json"},
                    # },
                    "LOG_FILE": logfile,
                    "ROBOTSTXT_OBEY":True,
                    "CONCURRENT_REQUESTS":10,
                    "ITEM_PIPELINES" : {
                        'mtworker.tasks.scrapy_tutorial.pipelines.ScrapyTutorialPipeline': 300,
                        'mtworker.tasks.scrapy_tutorial.pipelines.ScrapyPipeLine2': 400,
                        # 'mtworker.tasks.scrapy_tutorial.pipelines.PostgresDemoPipeline': 500,
                    },
                    "REQUEST_FINGERPRINTER_IMPLEMENTATION" : '2.7',
                    # 自定义settings
                    "MTX_ITEM_CALLBACK_URL":item_cb_url
                })
        if not hasattr(allSpiders, spider_name):
            return f"爬虫 {spider_name} 不存在"
        _spider = getattr(allSpiders,spider_name)
        process.crawl(PlaywrightDocSpider)
        process.start()
        print("domain_crawl finished")
    except Exception as e:
        print("启动爬网失败。。")
        traceback.print_exception(e)

    
        

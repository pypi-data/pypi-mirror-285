import os,sys,time
from mtworker.__main__ import app
from mtworker.TaskWorker import TaskWorker
import httpx
from celery import Celery
import logging
from mtworker.log import setup_custom_logger
logger = logging.getLogger(__name__)
from mtworker.tasks import *
from ..tasks import scrapy_demo
@app.command()
def scrapy1():
    try:
        scrapy_demo.run_spider("https://www.baidu.com")
    except Exception as e:
        print("出错")
        print(e)
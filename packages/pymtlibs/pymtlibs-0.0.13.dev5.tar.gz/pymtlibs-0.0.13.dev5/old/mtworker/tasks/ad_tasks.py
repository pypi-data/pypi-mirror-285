
from playwright.sync_api import sync_playwright
import os,time
from datetime import datetime
from celery import Celery
from kombu import Queue
import time
import time
import random
from playwright.sync_api import sync_playwright
from playwright.sync_api import Route, Response
from celery import shared_task
import httpx
import traceback
from celery import shared_task,chord, group, signature, uuid
from celery.signals import (
    after_setup_task_logger,
    task_success,
    task_prerun,
    task_postrun,
    celeryd_after_setup,
    celeryd_init,
)
from urllib.parse import urlparse

# targetUrl = "https://gamerushbin.blogspot.com/2022/12/the-top-10-best-meal-kit-delivery.html";
fakeHtml="""<html><body>
  <h1>fake html</h1>
  <iframe data-aa='2144138' src='//ad.a-ads.com/2144138?size=468x60' style='width:468px; height:60px; border:0px; padding:0; overflow:hidden; background-color: transparent;'></iframe>
</body></html>
"""

####
@shared_task(bind=True, name="tasks.aadView")
def aadView(self,**kwargs):
    """使用住宅ip浏览a-ad广告"""
    try:
        # 随机延时 搭配 定时任务固定的触发间隔，能做到看起来时间点随机。
        time.sleep(random.randint(0, 15))
        proxy_url = kwargs.get("proxyUrl")        
        proxy = None
        if proxy_url:
            uri = urlparse(proxy_url)
            proxy = {
                "server":f"http://{uri.hostname}:{uri.port}",
                "username": uri.username,
                "password": uri.password
            }
        targetUrl = kwargs.get("targetUrl")
        
        def handle_route_target_url(route: Route):
            route.fulfill(status=200, content_type="text/html", body=fakeHtml)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                proxy=proxy,
                timeout=60*1000
            )
            context = browser.new_context(
                http_credentials={"username": "bill", "password": "pa55w0rd"}
            )
            page = context.new_page()
            
            page.route(targetUrl, handle_route_target_url)
            print(f"准备打开目标网址： targetUrl {targetUrl}")
            page.goto(targetUrl)
            time.sleep(60)
            browser.close()
            # 提交任务结果
            httpx.post("https://local3502.yuepa8.com/api/taskpostback")
    except Exception as e:
        traceback.print_exception(e)

__all__ = ['ad_tasks', 'demo_tasks','scrapy_demo']


#!/usr/bin/env python3
# import typer
# import os,time
# from datetime import datetime
# from celery import Celery
# from kombu import Queue
# from celery.schedules import crontab
# import requests
# from celery import shared_task,chord, group, signature, uuid
# from celery.signals import (
#     after_setup_task_logger,
#     task_success,
#     task_prerun,
#     task_postrun,
#     celeryd_after_setup,
#     celeryd_init,
# )
# import time
# import sys
# from celery.utils.log import get_task_logger
# from celery import Celery
# import httpx
# from threading import Thread
# import logging
# import traceback
# logger = get_task_logger(__name__)
# app = Celery('tasks')

# # 导入其他模块定义的任务
# from .ad_tasks import *

# # @app.task
# @shared_task(bind=True)
# def mtworker_add(x, y):
#     return x + y

# @app.task
# def test(arg):
#     print(f"test task called arg: {arg}", )
#     return f"task result {arg}"

# # @app.task
# @shared_task(bind=True)
# def add(x, y):
#     print("add task called")
#     z = x + y
#     print(z)
# # @app.task
# @shared_task(bind=True)
# def hello_world():
#     return "Hello World!"

# # @app.task(bind=True)
# @shared_task(bind=True)
# def update_schedule(self):
#     """动态更新计划任务配置"""
#     try:
#         print("动态更新计划任务配置")
#         print('self')
#         print(self)
#         print(f'self.app', self.app)
#         response = httpx.get(os.environ.get("MTX_WORKER_API_URL") + "?type=schedule")
#         new_config = response.json()
#         print("new config")
#         print(new_config)
#         print("old config")
#         print(app.conf.beat_schedule)
        
#         # app.conf.update(beat_schedule = new_config["schedule"])
#         app.conf.beat_schedule=None
#         app.conf.update(beat_schedule = None)
#         print("app")
#         print(self)

#         print("应用新的计划任务配置")
#         print(new_config)
#     except Exception as e:
#         print("更新任务计划失败")
#         traceback.print_exception(e)

# # @app.on_after_configure.connect
# # def setup_periodic_tasks(sender, **kwargs):
# #     # 这里可以添加定时任务，不过，目前的设计定时计划的数据来自api后端，所以这里暂时不配置
# #     # print("setup_periodic_tasks")
# #     # # Calls test('hello') every 10 seconds.
# #     # sender.add_periodic_task(1, test.s('hello'), name='add every 1')

# #     # # Calls test('world') every 30 seconds
# #     # sender.add_periodic_task(30.0, test.s('world'), expires=10)

# #     # # Executes every Monday morning at 7:30 a.m.
# #     # sender.add_periodic_task(
# #     #     crontab(hour=7, minute=30, day_of_week=1),
# #     #     test.s('Happy Mondays!'),
# #     # )
# #     # print("setup_periodic_tasks")
# #     pass
    
    

# # app.conf.timezone = 'UTC'

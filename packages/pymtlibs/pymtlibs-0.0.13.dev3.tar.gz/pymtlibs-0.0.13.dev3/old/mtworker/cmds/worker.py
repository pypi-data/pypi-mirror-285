import os,sys,time
from mtworker.__main__ import app
from mtworker.TaskWorker import TaskWorker
import httpx
import logging

from mtworker.consts import ENV_NAME_APIURL
from mtworker.log import setup_custom_logger

logger = logging.getLogger(__name__)
@app.command()
def worker(api: str,beat: str=None):
    print(f"worker start with url: {api}")
    os.environ.setdefault(ENV_NAME_APIURL,api)
    setup_custom_logger('root')
    # push_log("日志消息11111，")
    logger.info("worker start.......")
    taskworker = TaskWorker(api)
    taskworker.start()
    print("所有任务完成了==============================================================")

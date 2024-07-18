#!/usr/bin/env python3
import sys, os, time
import typer
import json
import threading
import random
from datetime import datetime
from kombu import Queue
import requests

import httpx
from typing import Optional
import logging
from threading import Thread
from queue import Queue
# from lib.pool_workers import Pool
from mtworker.TaskWorker import TaskWorker
from time import sleep, perf_counter
import httpx
import logging

from mtworker.log import setup_custom_logger

app = typer.Typer()
from mtworker.cmds.setup import *
from mtworker.cmds.worker import *
from mtworker.cmds.celery_worker import *
from mtworker.cmds.scrapy1 import *



class Main:
    def __init__(self):
        pass
        
        
    def run(self):
        app()
        
def cli():
    main = Main()
    main.run()
if __name__ == "__main__":
    cli()
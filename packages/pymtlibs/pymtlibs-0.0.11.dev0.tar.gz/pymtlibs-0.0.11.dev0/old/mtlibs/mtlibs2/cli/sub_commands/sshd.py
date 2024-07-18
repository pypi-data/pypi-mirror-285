import asyncio
import os
from time import time
from git.repo import Repo
from pathlib import Path
from csservices import portforward
import time
from mtlibs import mtutils

def on_command(args):
    """启动ssh服务器"""
    print('启动ssh服务器')
    mtutils.init_sshd()
    os.system("sudo service ssh start")
    while True:
        time.sleep(1)

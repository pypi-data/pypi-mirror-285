#!/usr/bin/env python3
import sys
import os
from mtlibs.docker_helper import isInContainer
from mtlibs import process_helper
from pathlib import Path
import logging
from dotenv import load_dotenv, find_dotenv
from mtlibs.github import gitup
import time
import argparse  

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():    
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", default=None, nargs="*") 
    args = parser.parse_args()
    logger.info(f"urls: {args.urls}")
    
    
    urls = args.urls
    if not urls:
        # logger.info(f"没有输入urls参数，转为从环境变量中获取")
        # 从输入参数，或者环境变量中获取gitup网址。
        urls_from_env = os.environ.get("MTX_GITUP")
        if urls_from_env:
            urls = urls_from_env.split("|")
    
    if not urls:
        logger.info(f"need urls")
        time.sleep(3)
        exit()

    for item in urls:
        logfile = gitup(item)        
        # os.system(f"tail -f {logfile}")
    
    # while True:
    #     time.sleep(100)

if __name__ == "__main__":
    main()




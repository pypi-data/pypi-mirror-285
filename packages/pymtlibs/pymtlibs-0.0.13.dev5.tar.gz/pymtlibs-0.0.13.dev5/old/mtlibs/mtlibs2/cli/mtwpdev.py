#!/usr/bin/env python3

import os
import sys
import re
from version_parser import Version
from pathlib import Path
import shutil
from dotenv import load_dotenv, find_dotenv
import  argparse
import logging
from .. service.nginx import NginxService
from .. service.phpfpm import PhpFpmService

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """启动wordpress 开发环境"""
    cwd = os.getcwd()
    cwd_nginx_conf = os.path.join(os.getcwd(), "nginx.conf")
    if Path(cwd_nginx_conf).exists():
        logger.info(f"复制nginx.conf 文件到 /etc/nginx/nginx.conf")
        shutil.copy(cwd_nginx_conf, "/etc/nginx/nginx.conf")
    
    NginxService().start()
    # PhpFpmService.start()
    PhpFpmService().start()
    
    
    

if __name__ == "__main__":
    main()

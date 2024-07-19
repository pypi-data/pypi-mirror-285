import sys
import os
from mtlibs.docker_helper import isInContainer
from mtlibs import process_helper
from pathlib import Path
import logging
from os import path
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv
from mtlibs.github import gitup,gitParseOwnerRepo,gitclone
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_sshd():
    public_key = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDBYOFBjYyNpU/2gTpySjQz5WMMN9hfHRxQOAy1hPIGVpDncutkN67zXP2tBILbrxRNvltN3uO2fv3MV4scBDwV4z5AJfc9urlIvHrDfUYwhQVjqN/zza4aYKmIGi5b1B0Lve4/VSDqfjAaAhrPliWxx4mYUrLZREDwVyQocq6zuvUXkknNqr9/7TxCwNs37k7tSXPIpe+rbO2b+aADM3voq9ta30qaqO76HfA/R+YnfRtWth5uD+dYZy85mJPWD6Z6kOo4Uwb86pn8uf/yQ1ZyCDPp0P72feMKJGVgInM0jw+j44qlfOfXgq3MnjpBLEP7lZ2tC4MzMinvEdUpcNNxEjHNwsIKRxcAaiB0COc0rNNJLWoJndHO0IAqp1ZKjbRb+/Pco8WxL3Updkk23WZZgVyUtvI+wrmrDT4s73x/C28lQkWC+YLuKJOLKYAG2rvXaZifO1pFJE6pcvrP1ciXvjIG6YKIU6m9FrHZTz7CXgpy42p0SM8jqYODGfPVaEE= jamal@fabrikam.com
"""
    logger.info("设置并启动ssh服务")
    public_dir = os.path.join(os.path.expanduser('~'),".ssh/authorized_keys")
    if not Path(public_dir).exists():
        Path(public_dir).parent.mkdir(mode=0o600, exist_ok=True)
        Path(public_dir).touch(mode=0o600)
    
    
    with open(public_dir,'w') as f:
        f.write(public_key)
    process_helper.exec("service ssh start")

def setup_git():
    logger.info("设置git环境")
    os.system(f"git config --global user.email a@a.com")
    os.system(f"git config --global user.name a")
    
def setup_dockcer_env():
    logger.info("登录docker hub")
    DOCKER_HUB_USER=os.environ.get("DOCKER_HUB_USER")
    DOCKER_HUB_PASSWORD=os.environ.get("DOCKER_HUB_PASSWORD")
    os.system(f"""echo {DOCKER_HUB_PASSWORD} | docker login --username {DOCKER_HUB_USER} --password-stdin""")

def setup_gateway():
    """如果设置了代理网关，这将容器的默认网关ip设置为这个网关IP"""
    gateway_ip = os.environ.get("MTX_GATEWAY_IP")
    if gateway_ip:
        logger.info(f"网关IP: {gateway_ip}")
        os.system(f"ip route del default")
        os.system(f"route add default gw {gateway_ip}")
        
        logger.info("测试外网IP")
        os.system("curl --insecure ipinfo.io")
        logger.info(f"=====================================\n请查看上方的IP输出，看是否正确!!!, 如果出现dns问题，\n例如：无法解释域名等错误，请正确设置容器的DNS为: {gateway_ip}\n======================================\n")
    else:
        logger.info("没有指定代理网关，跳过网关设置")
        
def main():
    setup_gateway()
    giturl = os.environ.get("MTX_DEV_GIT")
    if not giturl:
        logger.info("no git url , skip clone")
    else:
        logger.info(f"gitup env: {giturl}")
        items = giturl.split("|")
        for item in items:
            logger.info(f"item: {item}")
            parsed = urlparse(giturl)
            owner,repo,file = gitParseOwnerRepo(giturl)
            clone_to = path.join(os.getcwd(),repo)
            logger.info(f"clone 到 {clone_to}")
            if Path(clone_to).exists():
                logger.info("target dir exists , skip clone")
            else:
                gitclone(owner,repo,parsed.username,clone_to)
                logger.info("clone finish")
   
    start_sshd()
    setup_git()
    logger.info("ready!")
    process_helper.exec("sleep infinity")
        
if __name__ == "__main__":
    main()

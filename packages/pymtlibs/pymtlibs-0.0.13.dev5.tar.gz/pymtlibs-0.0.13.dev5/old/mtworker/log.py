import logging
import httpx
import os

from mtworker.consts import ENV_NAME_APIURL
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    backendUrlBase = os.environ.get(ENV_NAME_APIURL)
    print(f"backendUrlBase:{backendUrlBase}")
    httpLogger = MyBackendLogHandler(f"{backendUrlBase}/api/log", "pylog")
    httpLogger.setLevel(logging.INFO)
    logger.addHandler(httpLogger)
    return logger

class MyBackendLogHandler(logging.StreamHandler):

    def __init__(self, url:str, topic):
        logging.StreamHandler.__init__(self)
        self.url = url
        self.topic = topic
    def emit(self, record):
        msg = self.format(record)
        httpx.post(self.url, data={
            "message":msg,
            "app": "mtworker",
            "level": record.levelno,
            "log_type": "pyloging"
        })
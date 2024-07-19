import asyncio
import logging
import os
import shlex
import subprocess
import tempfile
import traceback
from mtlibs import mtutils, process_helper
from mtlibs.mtutils import ranstr


logger = logging.getLogger(__name__)


class OpenvpnProc():
    """
        openvpn 服务进程
        说明： openvpn 服务入口点是openvpn.conf配置文件。
            而配置文件里面需要指定好几个证书，而且，还有客户端证书部分的处理比较复杂繁琐。
            目前的解决办法是，通过其他方式预先将证书生成。放到指定路径下。
            用：kylemanna/docker-openvpn
            1:添加客户端证书
            docker run -v /code/cli/data/openvpn:/etc/openvpn --rm -it kylemanna/openvpn easyrsa build-client-full client2 nopass
            2：获取客户端配置文件
            docker run -v /code/cli/data/openvpn:/etc/openvpn --rm -it kylemanna/openvpn ovpn_getclient main_win > /code/cli/data/ovpn/main_win.ovpn


        openvpn配置文件字段说明：
            [verb]: 日志输出的详细程度，9为最高，
    """

    def __init__(self):
        self.tmpdirname = tempfile.gettempdir() + "/openvpn_" + ranstr(20)

    def write_openvpnconfig(self):
        self.pki_base_path = os.path.abspath("./resources/gateway/openvpn/pki")
        self.ccd_path = os.path.abspath("./resources/gateway/openvpn/ccd")
        self.openvpn_config_path = self.tmpdirname + "/openvpn.conf"
        mtutils.writefile(self.openvpn_config_path, """
server 192.168.255.0 255.255.255.0
verb 3
key {key}
ca {ca_path}
cert {cert}
dh {dh_path}
tls-auth {tls_auth}
key-direction 0
keepalive 10 60
persist-key
persist-tun

proto udp
# Rely on Docker to do port mapping, internally always 1194
port 1194
dev tun0
status /tmp/openvpn-status.log

user nobody
group nogroup
comp-lzo no

client-to-client
verb 3
client-config-dir {ccd_path}

### Route Configurations Below
route 192.168.255.0 255.255.255.0
# route 75.126.135.131 255.255.255.255
#成功连接后添加主机路由信息(能让客户端自动设置路由表)
push "route 192.168.254.0 255.255.255.0"
#下面注释了的，是特定ip的路由设置（客户端）
# push "route 8.8.8.8 255.255.255.255"
# push "route 75.126.135.131 255.255.255.255"
### Push Configurations Below
# push "block-outside-dns"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
push "comp-lzo no"

""".format(
            key=os.path.join(self.pki_base_path,
                             "private/VPN.SERVERNAME.COM.key"),
            ca_path=os.path.join(self.pki_base_path, "ca.crt"),
            dh_path=os.path.join(self.pki_base_path, "dh.pem"),
            tls_auth=os.path.join(self.pki_base_path, "ta.key"),
            cert=os.path.join(self.pki_base_path,
                              "issued/VPN.SERVERNAME.COM.crt"),
            ccd_path=self.ccd_path,
        ).encode())

    async def handle_output(self):
        try:
            while True:
                if self.process.stdout:
                    line = self.process.stdout.readline().decode().strip()
                    logger.debug("vpn->{}".format(line))
                    # if line.strip().find('Initialization Sequence Completed') > 0:
                    #     return "ok"
                    # TODO: 捕获失败的字符串，返回
                    # 要不然，进程启动失败会卡住,协程一直不退出
                if self.process.stderr:
                    line = self.process.stderr.readline().decode()
                    logger.info("vpn->[error]{}".format(line))
                if self.process.poll() is not None:
                    break
        except Exception as e:
            logger.error(traceback.format_exc(e))

    async def start(self):
        """启动openvpn进程"""
        self.write_openvpnconfig()
        # 必要的初始化

        bash_init = """
mkdir -p /dev/net
if [ ! -c /dev/net/tun ]; then
    mknod /dev/net/tun c 10 200
fi"""
        process_helper.bash(bash_init)
        cmd = "openvpn --config " + self.openvpn_config_path
        self.process = subprocess.Popen(
            shlex.split(cmd), stdout=subprocess.PIPE)
        await self.handle_output()

import logging
import shlex
import subprocess
import tempfile
import traceback

from mtlibs import mtutils, process_helper
from mtlibs.mtutils import ranstr

logger = logging.getLogger(__name__)


class FrpcProc():
    """启动frpc隧道客户端"""

    def __init__(self, server_host, server_port, local_port):
        self.tmpdirname = tempfile.gettempdir() + "/frpcconfig_" + ranstr(20)
        self.server_host = server_host
        self.server_port = server_port
        self.local_port = local_port

    @classmethod
    def installIfNeed(cls):
        """安装"""
        if not process_helper.is_tool("frpc"):
            process_helper.bash("""
        wget -q -O frp_0.36.2_linux_386.tar.gz https://github.com/fatedier/frp/releases/download/v0.36.2/frp_0.36.2_linux_386.tar.gz && \
        tar vxzf frp_0.36.2_linux_386.tar.gz && rm frp_0.36.2_linux_386.tar.gz && \
        sudo cp frp_0.36.2_linux_386/frpc /usr/local/bin && sudo chmod +x /usr/local/bin/frpc && \
        sudo cp frp_0.36.2_linux_386/frps /usr/local/bin && sudo chmod +x /usr/local/bin/frps && \
        rm -rdf frp_0.36.2_linux_386
    """)

    def write_config(self):
        self.config_file = self.tmpdirname + "/frpc.ini"
        mtutils.writefile(
            self.config_file, """
[common]
protocol = tcp
server_addr = {server_host}
server_port = {server_port}

user = u3e108yisagtkocq
token = SakuraFrpClientToken
sakura_mode = true
use_recover = true

tcp_mux = true
pool_count = 1

[C74LB9FQ]
type = tcp
local_ip = 127.0.0.1
local_port = {local_port}
remote_port = 28176
use_encryption = false
use_compression = false""".format(server_host=self.server_host,
                                  server_port=self.server_port,
                                  local_port=self.local_port).encode())

    async def handle_output(self):
        try:
            while True:
                if self.process.stdout:
                    line = self.process.stdout.readline().decode().strip()
                    logger.debug("frpc->{}".format(line))
                if self.process.stderr:
                    line = self.process.stderr.readline().decode()
                    logger.info("frpc->[error]{}".format(line))
                if self.process.poll() is not None:
                    break
        except Exception as e:
            logger.error(traceback.format_exc(e))

    async def start(self):
        """启动openvpn进程"""
        # self.installIfNeed()
        FrpcProc.installIfNeed()
        self.write_config()
        cmd = "frpc --config " + self.config_file
        self.process = subprocess.Popen(shlex.split(cmd),
                                        stdout=subprocess.PIPE)
        await self.handle_output()

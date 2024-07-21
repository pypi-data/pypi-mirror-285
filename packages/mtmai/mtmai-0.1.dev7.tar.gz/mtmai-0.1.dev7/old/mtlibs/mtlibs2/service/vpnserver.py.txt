import os
from stem.util import term


def start():
    """
        启动 vpn 服务
    """
    # 目前有警告：ERROR: Cannot ioctl TUNSETIFF tun0: Device or resource busy (errno=16)
    # 但是毕竟还能用。
    print(term.format("启动 vpnserver", term.Color.RED), flush=True)
    os.system("bash -c './bin/start_vpnserver' ")


if __name__ == '__main__':
    start()
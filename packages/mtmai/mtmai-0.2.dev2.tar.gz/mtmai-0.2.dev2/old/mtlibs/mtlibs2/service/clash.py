
import os
from stem.util import term


def start():
    """
        启动 clash 代理服务，
        注意，这个代理提供的以然是tor网络出口。
    """
    print(term.format("启动 clash 服务", term.Color.RED), flush=True)

    os.system('cp -r ~/.config/clash /tmp/clash')

    with open('/tmp/clash/config.yaml', 'w') as f:
        f.write("""
# HTTP(S) and SOCKS5 server on the same port
mixed-port: 42080
# Port of SOCKS5 proxy server on the local end
# socks-port: 47891
# Transparent proxy server port for Linux and macOS (Redirect TCP and TProxy UDP)
# redir-port: 47892
# Transparent proxy server port for Linux (TProxy TCP and TProxy UDP)
# tproxy-port: 47893
# Port of HTTP(S) proxy server on the local end
# port: 47894

bind-address: '0.0.0.0'
allow-lan: true
external-controller: 0.0.0.0:49090
secret: "feihuo321"
mode: rule
log-level: debug
ipv6: false
interface-name: eth0

authentication:
    - "mt:feihuo321"
proxies:
  # tor-socks5
  - name: "local9050"
    type: socks5
    server: 127.0.0.1
    port: 9050
proxy-groups:
  - name: tor_group
    type: select
    proxies:
      - local9050
rules:
  # - IP-CIDR,127.0.0.0/8,tor_group
  # - IP-CIDR,10.12.12.0/24,tor_group #内网网段
  # MATCH 为默认
  - MATCH,tor_group
  # - MATCH,DIRECT
""")

    os.system("clash -f /tmp/clash/config.yaml &")


if __name__ == '__main__':
    start()
    
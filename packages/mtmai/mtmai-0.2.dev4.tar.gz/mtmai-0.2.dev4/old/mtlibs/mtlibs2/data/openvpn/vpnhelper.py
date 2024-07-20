#!/usr/bin/env python3

import os,sys
import subprocess
DEFAULT_PASSWORD='feihuo321'
# mitmproxy 透明代理端口
# trans_port=6744
# clash 透明代理端口
trans_port=7892
# print("vpnhelper.py",sys.argv)
print("注意，当前使用iptables-legacy 而不是nf-tables")
if 'up' == os.environ.get('script_type'):
    # 服务器启动事件
    print("服务器启动。。。。。。。。。。。。。。。。。。。。。")
elif 'down' == os.environ.get('script_type'):
    # 服务器启动事件
    print("服务器关闭。。。。。。。。。。。。。。。。。。。。。")

elif 'user-pass-verify' == os.environ.get('script_type'):
    # 登陆认证
    username = os.environ.get('username')
    password = os.environ.get('password')
    print(os.environ)
    print(f"用户名：{username}")
    if not password == DEFAULT_PASSWORD:
        print(f"登陆失败,密码不正确， {username}")
        exit(1)
    else:
        print(f"登录成功{username} ")
        exit(0)

elif 'client-connect' == os.environ.get('script_type'):
    # 新的客户端连接
    username = os.environ.get('username')
    ifconfig_pool_remote_ip = os.environ.get('ifconfig_pool_remote_ip')
    dev = os.environ.get('dev')
    route_network_1 = os.environ.get('route_network_1')
    route_network_2 = os.environ.get('route_network_2')
    print(f"用户名: {username}, dev {dev}, IP: {ifconfig_pool_remote_ip}")
    print(f"route_network_1: {route_network_1}, route_network_2 {route_network_2}")
    # 流量转发到clash透明代理端口

    iptable_cmd = f"""iptables -t nat -A PREROUTING -s {ifconfig_pool_remote_ip} -p tcp --syn -j REDIRECT --to-ports {trans_port}"""
    print("☀️ 设置Iptables: \n"+iptable_cmd)
    #########################################################################################################
    ## 坑：如果是根clash搭配，53端口没必要nat转发到5353.因为clash已经有相关的设置(clash.yaml dns字段)。
    subprocess.check_call(iptable_cmd, shell=True)
    # 删除 iptables-legacy -t nat -D PREROUTING -s 10.12.12.202 -p udp --dport 53 -j REDIRECT --to-ports 5353
    # iptables-legacy -t nat -D PREROUTING -s 10.12.12.202 -p tcp --syn -j REDIRECT --to-ports 7892

elif 'client-disconnect' == os.environ.get('script_type'):
    # 客户端断开  
    username = os.environ.get('username')
    ifconfig_pool_remote_ip = os.environ.get('ifconfig_pool_remote_ip')
    dev = os.environ.get('dev')
    route_network_1 = os.environ.get('route_network_1')
    route_network_2 = os.environ.get('route_network_2')
    print(f"用户名: {username}, dev {dev}, IP: {ifconfig_pool_remote_ip}")
    print(f"route_network_1: {route_network_1}, route_network_2 {route_network_2}")
    # 删除NAT iptables 规则
    print(f"删除客户端的iptables 规则 {ifconfig_pool_remote_ip}")
    subprocess.check_call(f"""
    #iptables -t nat -D PREROUTING -s {ifconfig_pool_remote_ip} -p udp --dport 53 -j REDIRECT --to-ports 5353
    iptables -t nat -D PREROUTING -s {ifconfig_pool_remote_ip} -p tcp --syn -j REDIRECT --to-ports {trans_port}
    """, shell=True)


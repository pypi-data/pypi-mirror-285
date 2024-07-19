#!/usr/bin/env python3
import logging
import paramiko
import os
from pathlib import Path
from paramiko import SSHClient
from mtlibs.sshClient import SshClient
from mtlibs.SSH import SSH
from dotenv import load_dotenv, find_dotenv
import argparse
import logging
from mtlibs.yaml import load_yaml_file
import json

APP_NAME = "mtdp"

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def loadConfig():
    config = load_yaml_file(os.path.join(f"./deploy/{APP_NAME}.yml"))
    # logger.info(f"config data: {config}")
    mtdp_config  = config[APP_NAME]
    if not mtdp_config:
        raise Exception("配置文件不正确")
    return mtdp_config

def sub_default(args):
    mtdp_config = loadConfig()
    logger.info(f"配置：{mtdp_config}")
    
    
    ssh_config = mtdp_config["target"]["config"]
    user_name = ssh_config["username"]
    password = ssh_config["password"]
    host=ssh_config["host"]
    port = ssh_config["port"]
    
    logger.info("connect begin")
    client = SshClient(host,port=port, password=password, user=user_name)
    connect_success = client.connect()
    if not connect_success:
        logger.debug(f"连接失败 {user_name}@{host}:{port}")
        
    # 范例：执行命令
    cmd = "ls -al /"
    output = client.exec_cmd(cmd)
    logger.info(f"输出 {output}")
    
    # # demo: 下载整个文件夹
    # remotefile, local_file = '/.dockerenv', '.tmp/dockerenv1'
    # client.sftp_get(remotefile, local_file)  # 下载文件    
    # client.sftp_get_dir("/root",".tmp/test1")   
	
    # 上传文件测试
    remotedir = "/app2"
    client.exec_cmd(f"mkdir {remotedir}")
    localdir = os.path.join(os.getcwd(),"deploy/uploads")    
    client.sftp_put_dir(localdir,remotedir)  # 上传文件夹
    
    # 释放资源
    client.close()
    
def main():
    print("mtdp  这个命令好像没用了。")
    parser = argparse.ArgumentParser(description="mtdp")
    parser.add_argument('dir',default=".", nargs="*")       
    #设置默认函数
    parser.set_defaults(func=sub_default)
    args = parser.parse_args()
    #执行函数功能
    args.func(args)


if __name__ == "__main__":
    main()
    
#!/usr/bin/env python3
# 用于docker build 文件的加密打包，容器启动的解密解压
import sys
import os
from docker_helper import isInContainer
import process_helper
from pathlib import Path
import logging
from dotenv import load_dotenv, find_dotenv
from github import gitup
import time
import argparse
import docker_helper
import os
import subprocess
from subprocess import run

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#默认密码
DEFAULT_BUNDlER_PASS="secret----DEFAULT_BUNDlER_PASS------19199";

def build_bundle(password):
    logger.info(f"在容器中，TODO，解压并运行主程序")
    curr_dir = os.getcwd()
    logger.info(f"开始压缩文件: {curr_dir}")
    cmd = f"""tar -czf /app.tar.gz ."""
    subprocess.run(cmd, shell=True)
    logger.info("开始加密")

    # 试试一次性压缩加密
    subprocess.run(f"tar -czf - . | gpg -c --passphrase {password} > /package.tar.gz.gpg", shell=True)


def container_up(password):
    logger.info(f"容器启动, 解密密码: {container_up} TODO: 解压运行")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("password", default=None, nargs="*")
    args = parser.parse_args()

    password = os.environ.get("MTX_BUNDLER_PASS",DEFAULT_BUNDlER_PASS)
    logger.info(f"密码: {password}")


    is_mtx_build = os.environ.get("MTX_DOCKER_BUILD",False)
    is_docker = docker_helper.is_docker()
    if not is_mtx_build:
        container_up(password)
    else:
        #构建阶段
        build_bundle(password)

    print(run("env"))
if __name__ == "__main__":
    main()




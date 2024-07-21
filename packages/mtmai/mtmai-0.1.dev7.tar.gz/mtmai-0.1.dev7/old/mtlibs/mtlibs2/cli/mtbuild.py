#!/usr/bin/env python3

##
## 运行当前项目默认构建任务
##
import os
import sys
import subprocess
from subprocess import run ,Popen
import shlex
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import argparse
import time
import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")

DOCKER_HUB_USER=os.environ.get("DOCKER_HUB_USER")
DOCKER_HUB_PASSWORD=os.environ.get("DOCKER_HUB_PASSWORD")
DOCKER_HUB_REGISTER=os.environ.get("DOCKER_HUB_REGISTER","")
IS_GITPOD = os.environ.get("USER") == "gitpod"

def login_dockerhub():
    if DOCKER_HUB_USER and DOCKER_HUB_PASSWORD:
        logger.info(f"登录dockerhub, 用户名: {DOCKER_HUB_USER}")
        cmd = f"echo {DOCKER_HUB_PASSWORD} | docker login {DOCKER_HUB_REGISTER} -u {DOCKER_HUB_USER} --password-stdin"
        logger.info(f"执行命令：{cmd}")
        run(cmd, check=True, shell=True)
    logger.info(f"没有指定docker hub 登录信息，跳过docker login")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", default=None, nargs="*", help="仓库地址, 如果指定了其他仓库，表示不是运行本项目的构建") 
    args = parser.parse_args()
    logger.info(f"urls: {args.urls}")

    urls = args.urls
    if not urls:
        # logger.info(f"没有输入urls参数，转为从环境变量中获取")
        # 从输入参数，或者环境变量中获取gitup网址。
        urls_from_env = os.environ.get("DOCKERBUILD_URL")
        if urls_from_env:
            urls = urls_from_env.split("|")

    else:
        logger.warn(f"远程构建暂时不支持")        
    #克隆到临时目录
    logger.info(f"[docker login]")
    login_dockerhub()
    run( shlex.split(f"pip3 install -U mtlibs"), check=True)
    if Path("./bin/build").exists():
        logger.info(f"docker build 使用脚本 ./bin/build")
        run(f"bin/build", check=True)

    # elif Path("./compose.yml"):
    #     logger.info(f"docker build 使用脚本: docker-compose build prebuild")
    #     run(shlex.split(f"docker-compose build prebuild"), check=True)
    #     run(shlex.split(f"docker-compose push prebuild"), check=True)
    else:
        logger.error(f"找不到 docker build 的相关脚本")


if __name__ == "__main__":
    main()

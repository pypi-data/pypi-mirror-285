#!/usr/bin/env python3
import os
import sys
import subprocess
import shlex
from dotenv import load_dotenv, find_dotenv
import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")


def main():
    items = {k: os.environ.get(k) for k in os.environ.keys()}
    docker_compose_addi_args = items.get("DOCKER_COMPOSE_ARGS","")
    argv = " ".join(sys.argv[1:])
    cmd = f"docker-compose {docker_compose_addi_args} {argv}"
    logger.info(f"执行命令：{cmd}")
    result2 = subprocess.run(shlex.split(cmd))
    if result2.returncode != 0:
        logger.error(f"exec with error {result2}")

if __name__ == "__main__":
    main()

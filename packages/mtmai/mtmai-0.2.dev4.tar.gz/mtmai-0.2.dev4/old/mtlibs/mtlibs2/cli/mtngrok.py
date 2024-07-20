#!/usr/bin/env python3
import logging
import paramiko
import os
from pathlib import Path
from paramiko import SSHClient
import shutil
# from mtlibs.sshClient import SshClient
# from mtlibs.SSH import SSH
from dotenv import load_dotenv, find_dotenv
import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")


def ngrok_install_ifneed():
    ngrok = shutil.which("ngrok")
    if not ngrok:
        os.system("""curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok""")
        
def ngrok_up_ssh():
    ngrok_install_ifneed()
    ngrok_authtoken = os.environ.get("NGROK_AUTHTOKEN")
    logger.info(f"ngrok token: {ngrok_authtoken}")
    # os.system(f"ngrok config add-authtoken {ngrok_token}")
    os.system(f"ngrok --authtoken {ngrok_authtoken} tcp 22")
    
def main():
    ngrok_up_ssh()
    
if __name__ == "__main__":
    ngrok_up_ssh()
    
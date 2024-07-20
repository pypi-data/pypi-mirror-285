#!/usr/bin/env python3
import sys
import os
from mtlibs.docker_helper import isInContainer
from mtlibs import process_helper
from pathlib import Path
import logging
from dotenv import load_dotenv, find_dotenv
import json
import logging
import shlex
import subprocess
import time
from os.path import relpath
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import re
from os import path
import argparse
from mtlibs.github import gitclone,gitParseOwnerRepo
from .. service.phpfpm import start_phpfpm
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info(f"启动phpfpm7.4")
    start_phpfpm()

if __name__ == '__main__':
    main()
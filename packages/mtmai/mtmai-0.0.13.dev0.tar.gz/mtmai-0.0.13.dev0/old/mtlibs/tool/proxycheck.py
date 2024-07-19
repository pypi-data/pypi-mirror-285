import argparse
import logging
import os
import sys
from urllib.parse import urlparse

import requests

from mtlibs import mtutils

logger = logging.getLogger(__name__)


def run_args(argv):
    parser = argparse.ArgumentParser(description="CLI")
    parser.add_argument('proxyurl', help='proxyurl')
    parser.set_defaults(func=run)
    args = parser.parse_args(argv)
    args.func(args)


def run(args):
    result = mtutils.proxyCheck(args.proxyurl)
    if result:
        print("代理服务 {} 活跃的".format(args.proxyurl))
    else:
        print("代理服务 {} 不活跃".format(args.proxyurl))

# 旧的设计是直接通过 http 传递参数和结果，不过后来发现celery-node 也能很好的兼容python celery 现在试试看好不好用
#
#

import os,sys,time
from mtworker.__main__ import app
from mtworker.TaskWorker import TaskWorker
import httpx
from celery import Celery
import logging
from mtworker.log import setup_custom_logger
logger = logging.getLogger(__name__)
from mtworker.tasks import *
  
@app.command()
def celery_worker(redis: str,beat: str=None):
    try:
        print(f"celery worker start with redis: {redis}")
        os.environ.setdefault("CELERY_BROKER_URL",redis)
        os.environ.setdefault("CELERY_RESULT_BACKEND",redis)
        
        celery_app = Celery('tasks', broker=redis, result_backend=redis)
        
        
        
        print("start celery app")
        celery_app.start(['worker','-l','DEBUG'])
        print("celery app started")
    except Exception as e:
        print("出错")
        print(e)

#!/usr/bin/env python3
import sys, os, time
import typer
import json
import threading
import random
from datetime import datetime
from celery import Celery
from kombu import Queue
import requests
from celery import shared_task,chord, group, signature, uuid
from celery.signals import (
    after_setup_task_logger,
    task_success,
    task_prerun,
    task_postrun,
    celeryd_after_setup,
    celeryd_init,
)
from celery.utils.log import get_task_logger
from celery import Celery
import httpx
from typing import Optional
import logging
from threading import Thread

from queue import Queue
# from ..lib.pool_workers import Pool
logger = get_task_logger(__name__)

# celery 原始启动命令参考：
# `celery -A mtxcms worker -l INFO`
# `celery -A mtxcms worker -l INFO -Q mtx_cloud`
# 这个命令的含义是：执行celery命令，从mtxcms模块中找到celery模块，并运行为工作进程。
app = typer.Typer()

def create_celery_app(api_url:str):
    response = httpx.get(api_url)
    print(f'params: {response.json()}')
    param = response.json()
    os.environ.setdefault("MTX_CELERY_BROKER",param["celery_broker"] )
    broker = param["celery_broker"]
    schedule = param['schedule']
    celery_app = Celery('tasks', broker=broker, result_backend=broker)
    # celery_app.conf.beat_schedule = {
    #     'add-every-3-seconds': {
    #         'task': 'mtworker.tasks.test',
    #         'schedule': 3.0,
    #         'args': ('test task--- args',)
    #     },
    # }
    
    # api 后端返回的计划任务配置（可以动态更改）
    celery_app.conf['CELERYBEAT_SCHEDULE'] = schedule
    
    return celery_app

# @app.command()
# def worker(api: str,beat: str=None):
#     """这个是使用celery 框架的入口点（过时）"""
#     os.environ.setdefault("MTX_WORKER_API_URL",api)
#     from mtworker.tasks import app as celery_app    
#     response = httpx.get(api)
#     print(f'params: {response.json()}')
#     param = response.json()
#     broker = param["broker"]
#     celery_app.conf.broker_url = broker
#     celery_app.conf.result_backend = broker
#     # 导入任务
#     import mtworker.tasks.ad_tasks
#     if beat:
#         # celery_app.start(['beat','-l','DEBUG', '--scheduler', 'mtworker.schedulers:MtxApiScheduler'])
#         celery_app.start(['worker','--beat','-l','DEBUG'])
#     else:
#         celery_app.start(['worker','-l','DEBUG'])

@app.command()
def worker(api: str,beat: str=None):
    """这个是使用celery 框架的入口点（过时）"""
    os.environ.setdefault("MTX_WORKER_API_URL",api)
    response = httpx.get(api)
    print(f'task data: {response.json()}')



def cli():
    app()

if __name__ == "__main__":
    app()

import os,sys,time
import httpx
import queue
import threading
from threading import Thread

from mtworker.consts import ENV_NAME_APIURL



class TaskWorker:
    def __init__(self, api_url:str):
        self.q = queue.Queue()
        self.api_url = api_url
        # 工作者消费者线程数
        self.thread_count = 0
        # 队列最大大小（决定了最大工作线程数）
        self.q_maxsize = 1

    def pull_task(self):
        """拉取新的任务"""
        while True:
            if self.q.qsize() > self.q_maxsize:
                # print("超过最大队列大小，跳过拉取")
                time.sleep(3)

            response = httpx.get(f"{os.environ.get(ENV_NAME_APIURL)}/api/task/get")
            params = response.json()
            if params:
                # print(f'新任务 task data: {response.json()}')
                self.q.put(params)
            else:
                time.sleep(2)

    def thread_comsume(self,payload):
        print(f"消费者线程 payload: {payload}")

    def dispatch_task(self):
        """消费者工作线程调用"""
        while True:
            payload = self.q.get()
            comsume_thread  =Thread(target=self.thread_comsume,args=(payload,))
            comsume_thread.start()
    def start(self):
        product_thread = Thread(target=self.pull_task)
        product_thread.start()
        self.dispatch_task()

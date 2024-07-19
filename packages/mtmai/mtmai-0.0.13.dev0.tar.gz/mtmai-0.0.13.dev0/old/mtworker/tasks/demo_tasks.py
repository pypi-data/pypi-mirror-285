from celery import Celery
import os,sys,time
from celery import shared_task

@shared_task(bind=True, name="tasks.add")
def add(self,x, y):
    return x + y

@shared_task(bind=True, name="tasks.add_kwargs")
def add_kwargs(self,a, b, c=0):
    return a + b 


from celery import Celery

celery = Celery('tasks', 
    broker='redis://',
    backend='redis://'
)

@celery.task(name='tasks.add')
def add(x, y):
    return x + y

@celery.task(name="tasks.add_kwargs")
def add_kwargs(a, b, c=0):
    # print(f"kwargs: {kwargs}")
    print(c)
    return a + b 

# 范例，练习
from fastapi import APIRouter, HTTPException
from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
from lib import hf
from transformers import DefaultDataCollator
from transformers import AutoModelForQuestionAnswering, TrainingArguments, Trainer
from openai import OpenAI
import os
from openai import OpenAI


router = APIRouter()
@router.get("/demo/openai1")
async def classifyDemo1():
    os.environ["OPENAI_API_KEY"]="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"
    client = OpenAI()
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
      ]
    )

    print(completion.choices[0].message)
    return {"message": "success"}

@router.get("/demo/openai-client1")
async def classifyDemo1():
    """作为客户端，对符合openai 接口的服务器发起请求（例子）"""
    client = OpenAI(
        api_key="1234",
        base_url="http://localhost:8201/v1", # change the default port if needed
    )

    # call API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "What is the meaning of life?",
            }
        ],
        model="llama3-70b-8192",
        stream=True
    )
    print(chat_completion)
    return {"message": "success"}


@router.get("/demo/mqdemo")
async def classifyDemo1():
    """基于 amqp 消息队列 简单例子"""
    import pika

    broker="amqp://admin:rzfpzBEJ@rabbitmq-161389-0.cloudclusters.net:19870"

    demoQueueName = "hello-test123"
    def demoAmqpSendMessage():
        # 连接到 RabbitMQ 服务器
        connection = pika.BlockingConnection(pika.URLParameters(broker))
        channel = connection.channel()

        # 声明一个队列
        channel.queue_declare(queue=demoQueueName)

        # 发送消息到队列
        channel.basic_publish(exchange='',
                            routing_key='hello',
                            body='Hello, RabbitMQ!')

        print(" [x] Sent 'Hello, RabbitMQ!'")

        # 关闭连接
        connection.close()

    def amqpDemoConsumeMessage():
        connection = pika.BlockingConnection(pika.URLParameters(broker))
        channel = connection.channel()

        # 声明队列
        queue_name = demoQueueName
        channel.queue_declare(queue=queue_name)

        # 回调函数，处理接收到的消息
        def callback(ch, method, properties, body):
            print(f" [x] Received {body}")

        # 告诉 RabbitMQ 使用 callback 处理从队列中接收到的消息
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit, press CTRL+C')

        # 开始监听队列
        channel.start_consuming()
    return {"message": "success"}



from transformers import pipeline
from huggingface_hub import notebook_login, login
import os

def loginHuggingface():
  """登录huggingface"""
  hfToken=os.getenv("HF_TOKEN")
  a = login(token=hfToken)
  print("登录结果", a)

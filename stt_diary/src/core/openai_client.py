# src/core/openai_client.py
import os
from openai import OpenAI

# .env에 OPENAI_API_KEY 저장해두면 알아서 읽음
# 필요하면 이렇게도 가능: OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI()

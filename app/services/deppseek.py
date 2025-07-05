from openai import OpenAI
import os
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app

class DeepSeek:

   

    @staticmethod
    def analysis(messages :list):
         # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        api_key = current_app.config['DEEPSEEK_API_KEY']
        base_url = current_app.config['DEEPSEEK_BASE_URL']
        prompt = current_app.config['DEEPSEEK_PROMPT']

        # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        client = OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": ""},
            ],
            stream=False
        )
        return response.choices[0].message.content
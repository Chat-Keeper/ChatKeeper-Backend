from openai import OpenAI
import requests
import os
import re
import ast
import json
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app




class DeepseekService:

    @staticmethod
    def is_valid_deepseek_reply(text: str) -> bool:
        """
        判断 DeepSeek 返回的 text 是否为正常的分析结果，而不是报错提示。
        """
        if not text or not text.strip():
            return False

        # 1. 黑名单：常见错误提示关键词
        error_indicators = [
            "服务器繁忙",
            "Service unavailable",
            "网络错误",
            "异常",
            "请稍后再试",
            "timeout",
        ]
        for err in error_indicators:
            if err.lower() in text.lower():
                return False

        #比如你期望返回必须包含 “Identity:” “tags:” “description:”
        required_fields = ["identity", "tags", "description"]
        lower = text.lower()
        if not all(field + ":" in lower for field in required_fields):
            return False

        #防止极短输出
        if len(text) < 20:
            return False

        return True
    
    @staticmethod
    def generate(content):
        #import os
        os.environ["NO_PROXY"] = "api.deepseek.com"  # 禁用代理
        API_KEY = "sk-4ea4ac74dc8d4d3ea512c9be9a4a3dfb" 

        # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        API_KEY = current_app.config['DEEPSEEK_API_KEY']
        BASE_URL = current_app.config['DEEPSEEK_BASE_URL']
        prompt = current_app.config['DEEPSEEK_PROMPT']

        client = OpenAI(api_key = 'sk-4ea4ac74dc8d4d3ea512c9be9a4a3dfb', base_url = "https://api.deepseek.com/v1")
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages = [
                {"role": "system", "content": prompt}, 
                {"role": "user", "content": content}
            ],
            stream=False
        )

        #异常检测
        if not response.choices or not response.choices[0].message.content:
            raise ConnectionError
        result = response.choices[0].message.content
        if not DeepseekService.is_valid_deepseek_reply(result):
            raise ConnectionError
        
        return result
        '''
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-reasoner",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        return response.text
    @staticmethod
    def analysis(user_id, group_id, speaker_id):
        '''
        info = [
            {
                'time_str':
                'speaker_name':
                'speaker_qq':
                'content':
            }
        ]
        '''
        #局部导入，防止循环导入
        from app.models.group import Group
        from app.models.speaker import Speaker
        speaker = Speaker.find(user_id, speaker_id)
        if speaker is None:
            raise RuntimeError
        group = Group.find(user_id, group_id)
        if group is None:
            raise RuntimeError
        info = Group.acquire(user_id, group_id, speaker_id)
        if info is None:
            raise RuntimeError
        #定义输出格式要求,确定输出内容
        output_format = (
            "identity: [i_e, n_s, t_f, p_j], 其中每个元素是 0-100 范围内的 integer\n"
            "tags: [], 一个含有 3-5 个关键词的列表，元素为字符串\n"
            "description: 一个长度为 300-500 的字符串"
        )
        #将之前的分析结果转换为字符串
        if speaker['analyzed'] == True:
            analysis_dict = {
                'identity': speaker['identity'],
                'tags': speaker['tags'],
                'description': speaker['description']
            }
            pre_analysis = (
                f"Identity: {analysis_dict['identity']}\n"
                f"tags: {json.dumps(analysis_dict['tags'], ensure_ascii=False)}\n"
                f"description: \"{analysis_dict['description']}\"\n"
            )
            instructions = (
            "并结合你上次的分析结果：\n"
            f"{pre_analysis}"
            "对于你的回答格式，要求你生成格式如下：\n"
            f"{output_format}"
            )
        else:
            instructions = (
            "对于你的回答格式，要求你生成格式如下：\n"
            f"{output_format}"
            )

        #构造聊天记录字符串
        user_messages = "\n".join(
            f"[{msg['time_str']}] {msg['speaker_name']} ({msg['speaker_qq']}): {msg['content']}"
            for msg in info
        )
        default_prompt = current_app.config['DEFAULT_ANALYSIS_PROMPT']
        content = (
            f"{default_prompt}\n\n"
            f"{instructions}\n\n"
            f"聊天记录如下：\n{user_messages}"
        )

        s = DeepseekService.generate(content)

        #将结果转换为python类型，识别包含空格，换行
        # 1. 预编译正则
        PAT_ID = re.compile(
            r"Identity:\s*(\[\s*[0-9]+(?:\s*,\s*[0-9]+)*\s*\])",
            flags=re.IGNORECASE | re.MULTILINE
        )
        PAT_TAGS = re.compile(
            r"tags:\s*(\[\s*\"[^\"]+\"(?:\s*,\s*\"[^\"]+\")*\s*\])",
            flags=re.IGNORECASE | re.MULTILINE
        )
        PAT_DESC = re.compile(
            r"description:\s*\"([\s\S]{1,1000}?)\"",
            flags=re.IGNORECASE | re.MULTILINE
        )
        #提取文本
        m_id = PAT_ID.search(s)
        if m_id:
            identity = ast.literal_eval(m_id.group(1))

        m_tags = PAT_TAGS.search(s)
        if m_tags:
            tags = ast.literal_eval(m_tags.group(1))

        m_desc = PAT_DESC.search(s)
        description = m_desc.group(1).strip() if m_desc else ""

        result = {
            "Identity": identity,
            "tags": tags,
            "description": description
        }

        #更新speaker和group中speakers中的analyzed
        Speaker.update(user_id, speaker_id, result)
        Group.update(user_id, group_id, speaker_id)

        speaker = Speaker.find(user_id, speaker_id)
        return{
            'speaker_id': speaker['speaker_id'],
            'speaker_name': speaker['speaker_name'],
            'speaker_qq': speaker['speaker_qq'],
            'analyzed': speaker['analyzed'],
            'identity': speaker['identity'],
            'tags': speaker['tags'],
            'description': speaker['description']
        }
    @staticmethod
    def get_keywords(keyword):

        description = keyword + '\n根据我给你的关键词，生成与这个关键词意思相近的100个关键词\n'
        #定义输出格式要求,确定输出内容
        output_format = "keyword_list: ['', '', ''], 其中每个元素是一个关键词\n"
        instructions = (
            "对于你的回答格式，要求你生成格式如下：\n"
            f"{output_format}"
        )
        content = (
            f"{description}\n\n"
            f"{instructions}\n\n"
        )
        str = DeepseekService.generate(content)
        # 提取列表部分并转换
        keyword_list = eval(str.split(': ')[1])
        return keyword_list
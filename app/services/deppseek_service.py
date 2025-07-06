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

        if "result" not in text.lower():
            return False

        if len(text) < 20:
            return False

        return True
    
    @staticmethod
    def generate(content):

        # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        API_KEY = current_app.config['DEEPSEEK_API_KEY']
        BASE_URL = current_app.config['DEEPSEEK_BASE_URL']
        prompt = current_app.config['DEEPSEEK_PROMPT']

        client = OpenAI(api_key = API_KEY, base_url = BASE_URL)
        response = client.chat.completions.create(
            model="deepseek-chat",
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
        
        return response.choices[0].message.content
        
    @staticmethod
    def analysis(user_id, group_id, speaker_id):

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

        analysis_prompt = """\
    请你按照以下要求，只输出类似实例输出的pyhton代码，即一个符合Python语法的字典：
    identity:  
    - 一个包含以下四个成员的字典：
    - i_e (Introversion–Extraversion)：0–100 之间的整数，数值越大表示越偏向外向  
    - n_s (Intuition–Sensing)：0–100 之间的整数，数值越大表示越偏向直觉  
    - t_f (Thinking–Feeling)：0–100 之间的整数，数值越大表示越偏向情感  
    - p_j (Perceiving–Judging)：0–100 之间的整数，数值越大表示越偏向判断  

    tags:  
    - 一个长度为 8-10 的列表，包含描述用户性格特征或兴趣爱好的关键词，如“幽默”、“严谨”、“户外运动爱好者”等  

    description:  
    - 用 300–500 字的连贯段落，结合上述 MBTI 维度与标签，为用户画像作详细阐述  
    - 要点可包括：  
    1. 性格倾向如何影响其日常行为  
    2. 兴趣爱好对其社交或职业的意义  
    3. MBTI 四个维度综合后呈现出的典型特点  

    示例输出：
    result = {
        identity: { i_e: 34, n_s: 76, t_f: 45, p_j: 82 },
        tags: ['幽默', '好奇心强', '数据驱动', '阅读爱好者'],
        description: '该用户具有较高的开放性与外向性，...（300–500 字）...'
    }
                
    """

        #将之前的分析结果转换为字符串
        if speaker['analyzed'] == True:
            analysis_dict = {
                'identity': speaker['identity'],
                'tags': speaker['tags'],
                'description': speaker['description']
            }
            identity = analysis_dict['identity']
            tags = analysis_dict['tags']
            description = analysis_dict['description']
            pre_analysis = (
                f"identity: {{ i_e: {identity['i_e']}, n_s: {identity['n_s']}, "
                f"t_f: {identity['t_f']}, p_j: {identity['p_j']} }}\n"
                f"tags: {tags}\n"
                f"description: '{description}'"
            )
            instructions = (
            "并结合你上次的分析结果：\n"
            f"{pre_analysis}"
            f"{analysis_prompt}"
            )
        else:
            instructions = (
            f"{analysis_prompt}"
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

        str = DeepseekService.generate(content)
        #return str
        start = str.find('{')
        end = str.rfind('}')
        s = str[start:end+1]
        result = ast.literal_eval(s)

        
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

        description = '根据我给你的关键词，生成与这个关键词意思相近的100个关键词\n'
        #定义输出格式要求,确定输出内容
        output_format = """\
        请你按照以上要求，只输出类似实例输出的pyhton代码，即一个符合Python语法的字典：
        实例输出：
        result = ['善良'， '热情'，'乐于助人']
        """
        content = (
            f"关键词为：{keyword}"
            f"{description}\n\n"
            f"{output_format}\n\n"
        )
        str = DeepseekService.generate(content)
        
        start = str.find('[')
        end = str.rfind(']')
        s = str[start:end+1]
        result = ast.literal_eval(s)
        
        return result
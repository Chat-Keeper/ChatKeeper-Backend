from openai import OpenAI
import os
import re
import ast
import json
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from app.models.speaker import Speaker
from app.models.group import Group


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
        # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        api_key = current_app.config['DEEPSEEK_API_KEY']
        base_url = current_app.config['DEEPSEEK_BASE_URL']
        prompt = current_app.config['DEEPSEEK_PROMPT']

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
            stream=False
        )

        #异常检测
        if not response.choices or not response.choices[0].message.content:
            raise ConnectionError
        s = response.choices[0].message.content
        if not DeepseekService.is_valid_deepseek_reply(s):
            raise ConnectionError
        
        return s

    @staticmethod
    def analysis(user_id, group_id, speaker_id,  info :list):
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
        speaker = Speaker.find(user_id, speaker_id)
        if speaker is None:
            raise RuntimeError

        #将之前的分析结果转换为字符串
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

        #定义输出格式要求,确定输出内容
        output_format = (
            "identity: [i_e, n_s, t_f, p_j], 其中每个元素是 0-100 范围内的 integer\n"
            "tags: [], 一个含有 3-5 个关键词的列表，元素为字符串\n"
            "description: 一个长度为 300-500 的字符串"
        )
        instructions = (
            "并结合你上次的分析结果：\n"
            f"{pre_analysis}"
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
        pass
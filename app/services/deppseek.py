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


class DeepSeek:

    @staticmethod
    def analysis(user_id, speaker_id, info :list):
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
            return None
         # 初始化 OpenAI 客户端（DeepSeek兼容 OpenAI API）
        api_key = current_app.config['DEEPSEEK_API_KEY']
        base_url = current_app.config['DEEPSEEK_BASE_URL']
        prompt = current_app.config['DEEPSEEK_PROMPT']
        default_prompt = current_app.config['DEFAULT_ANALYSIS_PROMPT']

        client = OpenAI(api_key=api_key, base_url=base_url)

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
        content = (
            f"{default_prompt}\n\n"
            f"{instructions}\n\n"
            f"聊天记录如下：\n{user_messages}"
        )

        s = " "
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
                stream=False
        )
            #检查返回的响应是否有效
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No valid response content")
            s = response.choices[0].message.content

        except Exception as e:
            # 捕获网络错误、API 错误或其他异常"
            return None
        
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
            try:
                identity = ast.literal_eval(m_id.group(1))
            except (SyntaxError, ValueError):
                identity = []
        else:
            identity = []

        # 3. 提取 tags 列表
        m_tags = PAT_TAGS.search(s)
        if m_tags:
            try:
                tags = ast.literal_eval(m_tags.group(1))
            except (SyntaxError, ValueError):
                tags = []
        else:
            tags = []

        # 4. 提取 description 文本
        m_desc = PAT_DESC.search(s)
        description = m_desc.group(1).strip() if m_desc else ""

        result = {
            "Identity": identity,
            "tags": tags,
            "description": description
        }

        Speaker.update(user_id, speaker_id, result)
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
import os
from datetime import datetime
from flask import current_app
from app.services.chat_parser import ChatLogParser
from app.models.group import Group

class DataService:
    @staticmethod
    def chat_log_upload(user_id: str, group_id: str, file_path: str):
        """
        处理上传的聊天记录文件
        参数:
            user_id: 用户ID
            group_id: 群组ID
            file_path: 上传文件的完整路径
        """
        parser = ChatLogParser(file_path)
        messages = parser.parse_messages()
        Group.upload(group_id, user_id, messages)
        return messages
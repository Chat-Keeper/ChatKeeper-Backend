import os
from datetime import datetime
from flask import current_app
from app.services.chat_parser import ChatLogParser
from app.models.group import Group
from app.models.user import User
from app.models.speaker import Speaker

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
        result = Group.upload(user_id, group_id, messages)
        return result

    @staticmethod
    def create_new_group(user_id: str, group_name: str) -> bool:
        user = User.find_id(user_id)
        if user is None:
            return False
        else:
            Group.create(user_id, group_name)
        return True
    
    @staticmethod
    def rename_group(user_id: str, group_id: str, group_name: str) -> bool:
        group = Group.find(user_id, group_id)
        if group is None:
            return False
        else:
            Group.rename(user_id, group_id, group_name)
            return True
        

    @staticmethod
    def list_all_speaker(user_id: str) -> list:
        user = User.find_id(user_id)
        if user is None:
            return None
        else:
            return Speaker.list(user_id)

    @staticmethod
    def get_speaker_detail(user_id: str, speaker_id: str) -> dict:
        speaker = Speaker.find(user_id, speaker_id)
        if speaker is None:
            return None
        else:
            return Speaker.get(user_id, speaker_id)

    @staticmethod
    def list_all_group(user_id: str) -> list:
        user = User.find_id(user_id)
        if user is None:
            return None
        else:
            return Group.list(user_id)

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
        result = Group.upload(group_id, user_id, messages)
        return messages

    @staticmethod
    def create_new_group(user_id: str, group_name: str) -> bool:
        pass

    @staticmethod
    def rename_group(user_id: str, group_id: str, group_name: str) -> bool:
        pass

    @staticmethod
    def list_all_speaker(user_id: str) -> list:
        pass

    @staticmethod
    def get_speaker_detail(user_id: str, speaker_id: str) -> dict:
        pass

    @staticmethod
    def list_all_group(user_id: str) -> list:
        pass

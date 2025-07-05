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
        try:
            messages = parser.parse_messages()
        except ValueError as v:
            raise ValueError("Unable to decode file, please use UTF-8 format")
        except Exception as e:
            raise ValueError(str(e))
        result = Group.upload(user_id, group_id, messages)
        if result is None:
            raise RuntimeError("Failed to save data in database")
        return result

    @staticmethod
    def create_new_group(user_id: str, group_name: str) -> str | None:
        group = Group.create(user_id, group_name)
        if group:
            return group["group_id"]
        else:
            return None

    @staticmethod
    def rename_group(user_id: str, group_id: str, group_name: str) -> bool:
        group = Group.find(user_id, group_id)
        if group is None:
            return False
        else:
            Group.rename(user_id, group_id, group_name)
            return True

    @staticmethod
    def list_all_speaker(user_id: str) -> list | None:
        user = User.find_id(user_id)
        if user is None:
            return None
        else:
            return Speaker.list(user_id)

    @staticmethod
    def get_speaker_detail(user_id: str, speaker_id: str) -> dict | None:
        speaker = Speaker.find(user_id, speaker_id)
        if speaker is None:
            return None
        else:
            return Speaker.get(user_id, speaker_id)

    @staticmethod
    def list_all_group(user_id: str) -> list | None:
        user = User.find_id(user_id)
        if user is None:
            return None
        else:
            return Group.list(user_id)

    @staticmethod
    def delete_group(user_id: str, group_id: str) -> bool:
        return Group.destroy(user_id, group_id)

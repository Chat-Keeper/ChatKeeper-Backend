from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy

Mongo = LocalProxy(lambda: current_app.mongo)

class Group:
    '''
    {
            "group_id": group_id,
            "user_id": user_id,
            "start_time"
            "group_name'
            "end_time": datetime.utcnow(),
            "message_num": len(messages),
            "speakers":    #字典组成的列表
            "messages":    #字典组成的列表
                {
                    "time":
                    "name":
                    "account":
                    "content":
                }
    }
    '''
    '''
    @staticmethod
    def create(group_name):
        return group


    @staticmethod
    def find(group_id)
        return group

    @staticmethod
    def rename(group_id, newname)
        return group

    @staticmethod
    def list()
        return speaker_list

    @staticmethod
    def upload(user_id, group_id, messages :list)
        return data
    @staticmethod
    def speaker_find(group_id, speaker_id) 
    
    
    

'''
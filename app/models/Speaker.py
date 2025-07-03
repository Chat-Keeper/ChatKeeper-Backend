from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy

Mongo = LocalProxy(lambda: current_app.mongo)

class Speaker:

    '''
    {
        "uesr_id": chat_id,
        "group_id": user_id,
        'speaker_id': speaker_id
        'speaker_name':
        'speaker_qq':
        "analyzed"
        "last_analyzed_at": 
        "personality":    #列表
        "interest":       #列表
    }
    '''
'''
    @staticmethod
    def create()->bool

    @staticmethod   
    def find()
        
    @staticmethod
    def list()
'''
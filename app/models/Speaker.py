from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy
from pymongo.errors import DuplicateKeyError

Mongo = LocalProxy(lambda: current_app.mongo_db)

class Speaker:


    
    @staticmethod
    def create(user_id, message) -> dict:
        qq = message['speaker_qq']
        existing = Mongo.speakers.find_one({'speaker_qq': qq})
        if existing:
            return existing

        speaker_id = str(uuid4())
        doc = {
            "user_id": user_id,
            "speaker_id": speaker_id,
            "speaker_name": message.get('speaker_name') or "",
            "speaker_qq": qq,
            "analyzed": False,
            "tags": [],
            "last_analyzed_at": None,
            "personality": [],
            "description": ""
        }

        try:
            Mongo.speakers.insert_one(doc)
        except DuplicateKeyError:
            # 并发冲突时，什么也不做，下面再去取
            pass

        # 不管是新插还是碰撞，都从库里再查一次——一定得到一个 dict
        return Mongo.speakers.find_one({'speaker_qq': qq})

    
    @staticmethod
    def find(user_id, speaker_id):
        speaker = Mongo.speakers.find_one({'user_id': user_id, 'speaker_id': speaker_id})
        if speaker is None:
            return None
        return speaker

    @staticmethod
    def list(user_id):
        user = Mongo.users.find_one({'user_id': user_id})
        if user_id is None:
            return None
        data = list(Mongo.speakers.find({'user_id': user_id}, {
            'speaker_id': 1, 
            'speaker_name': 1,
            'speaker_qq': 1, 
            'analyzed': 1
        }))
        result = {'speaker_num': len(data)}
        result['speaker_info'] = data
        return result
    
    @staticmethod
    def get(user_id, speaker_id):
        speaker = Mongo.speakers.find_one({'user_id': user_id, 'speaker_id': speaker_id}, {'user_id': 0, 'last_analyzed_at': 0})
        if speaker is None:
            return None
        return speaker

from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy
from pymongo.errors import DuplicateKeyError

Mongo = LocalProxy(lambda: current_app.mongo_db)

class Speaker:
    
    @staticmethod
    def create(user_id, new_info) -> dict:
 
        speaker_id = str(uuid4())
        Mongo.speakers.insert_one({
            "user_id": user_id,
            "speaker_id": speaker_id,
            "speaker_name": new_info['speaker_name'],
            "speaker_qq": new_info['speaker_qq'],
            "analyzed": False,
            "last_analyzed_at": None,
            "tags": [],
            'identity': {
                "i_e": 0,
                "n_s": 0,
                "t_f": 0,
                "p_j": 0
            },
            "description": " "
        })
        result = Mongo.speakers.find_one({
            'user_id': user_id,
            'speaker_qq': new_info['speaker_qq'],
            'speaker_name': new_info['speaker_name']
        })
       
        return result

    
    @staticmethod
    def find(user_id, speaker_id):
        speaker = Mongo.speakers.find_one({'user_id': user_id, 'speaker_id': speaker_id})
        if speaker is None:
            return None
        return speaker

    @staticmethod
    def list(user_id):
        user = Mongo.users.find_one({'user_id': user_id})
        if user is None:
            return None
        data = list(Mongo.speakers.find({'user_id': user_id}, 
        {   '_id': 0,
            'speaker_id': 1, 
            'speaker_name': 1,
            'speaker_qq': 1, 
            'analyzed': 1
        }))
        data.append(len(data))
        return data
    
    @staticmethod
    def get(user_id, speaker_id):
        speaker = Mongo.speakers.find_one({'user_id': user_id, 'speaker_id': speaker_id}, {'user_id': 0, 'last_analyzed_at': 0, '_id': 0})
        if speaker is None:
            return None
        return speaker
    
    @staticmethod
    def update(user_id, speaker_id, feature: dict) -> bool:

        speaker = Mongo.speakers.find_one({'user_id': user_id, 'speaker_id': speaker_id})
        if speaker is None:
            return False

        Mongo.speakers.update_one(
            {'user_id': user_id, 'speaker_id': speaker_id},
            {'$set': {
                'analyzed': True,
                'last_analyzed_at': datetime.utcnow(),
                'tags': feature['tags'],
                'identity': feature['identity'],
                'description': feature['description']
            }}
        )
        return True
        


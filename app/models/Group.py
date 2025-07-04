from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy
from app.models.speaker import Speaker

Mongo = LocalProxy(lambda: current_app.mongo_db)

class Group:


    @staticmethod
    def create(user_id, group_name):
        #user = Mongo.users.find_one({'user_id': user_id})
        result = Mongo.groups.find_one({'user_id': user_id, 'group_name': group_name})
        if result is not None:
            return None
        group_id = str(uuid4())
        Mongo.groups.insert_one({
            'user_id': user_id,
            'group_id': group_id,
            'group_name': group_name,
            'start_time': None,
            'end_time': None,
            'message_num': 0,
            'speaker_num': 0,
            'speakers': [],
            'messages': []
        })
        result = Mongo.groups.find_one({'user_id': user_id, 'group_name': group_name})
        return result

    @staticmethod
    def find(user_id, group_id):
        result = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        if result is None:
            return None
        return result

    @staticmethod
    def rename(user_id, group_id, newname):
        result = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        if result is None:
            return None
        Mongo.groups.update_one(
            {"group_id": group_id},  # 集合里存储的也是字符串
            {"$set": {"group_name": newname}}
        )
        result = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        return result

    @staticmethod
    def speaker_find(group_id, speaker_id):
        group = Mongo.groups.find_one({'group_id': group_id})
        if group is None:
            return None
        result = Mongo.speakers.find_one({'speaker_id': speaker_id})
        if result is None:
            return None
        return result
    
    @staticmethod
    def list(user_id):
        user = Mongo.groups.find_one({'user_id': user_id})
        if user is None:
            return None
        data = list(Mongo.groups.find({'user_id': user_id}, {'user_id': 0, 'messages': 0, '_id':0}))
        data.append(len(data))
        return data


    @staticmethod
    def upload(user_id, group_id, messages: list):
        group = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        if group is None:
            return None
        user = Mongo.users.find_one({'user_id': user_id})
        if user is None:
            return None
        info = {
            'user_id': user_id,
            'upload_time': datetime.utcnow()
        }
        if len(messages) == 0:
            return None
        group['messages'].append(info)
        group['messages'].append(messages)
        group['message_num'] += len(messages)

        # 更新时间
        if group['start_time'] is None:
            group['start_time'] = messages[0]['time_str']
            group['end_time'] = messages[-1]['time_str']
        else:
            time_format = "%Y-%m-%d %H:%M:%S"
            start = datetime.strptime(group['start_time'], time_format)
            end = datetime.strptime(group['end_time'], time_format)
            curr_start = datetime.strptime(messages[0]['time_str'], time_format)
            curr_end = datetime.strptime(messages[-1]['time_str'], time_format)
            if curr_start < start:
                start = curr_start
            if curr_end > end:
                end = curr_end
            start_str = start.strftime(time_format)
            end_str = end.strftime(time_format)
            group['start_time'] = start_str
            group['end_time'] = end_str

        # 更新speakers列表
        for message in messages:
            value = message['speaker_qq']
            index = next((i for i, d in enumerate(group['speakers']) if d.get('speaker_qq') == value), None)
            
            if index is not None:
                group['speakers'][index]['speaker_msg_freq'] += 1
            else:
                group['speaker_num'] += 1
                new_info = {
                    'speaker_name': message['speaker_name'],
                    'speaker_qq': message['speaker_qq']
                }
                speaker = Speaker.create(user_id, new_info)  # 返回一个字典
                
                new_speaker = {
                    'speaker_id': speaker['speaker_id'],
                    'speaker_name': speaker['speaker_name'],
                    'speaker_qq': speaker['speaker_qq'],
                    'analyzed': speaker['analyzed'],
                    'speaker_msg_freq': 1
                }
                group['speakers'].append(new_speaker)

        #更新数据库中group
        Mongo.groups.update_one(
            {'user_id': user_id, 'group_id': group_id},
            {'$set': {
                'messages': group['messages'],
                'message_num': group['message_num'],
                'start_time': group['start_time'],
                'end_time':   group['end_time'],
                'speakers':   group['speakers'],
                'speaker_num':group['speaker_num'],
            }}
         )
        

        data = {
            'group_id': group['group_id'],
            'group_name': group['group_name'],
            'speaker_num': group['speaker_num'],
            'speaker_list': group['speakers'],
            'start_time': group['start_time'],
            'end_time': group['end_time'],
            'message_num': group['message_num']
        }

        return data

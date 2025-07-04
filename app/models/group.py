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
        '''
        Mongo.groups.insert_one({
            'user_id': str,
            'group_id': str,
            'group_name': str,
            'start_time': str,
            'end_time': str,
            'message_num': int
            'speaker_num': int
            'speakers': [{
                    'speaker_id': str,
                    'speaker_name': str,
                    'speaker_qq': str,
                    'analyzed': bool,
                    'speaker_msg_freq': int
                }],
            'messages': [{
                    'time_str': str,
                    'speaker_name': str,
                    'speaker_qq': str,
                    'content': str
                }]
        })
        '''
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


    @staticmethod  #重构, 每天聊天记录分开存，上传的同时实现更新（如两次上传有时间重叠要去重）!
    def upload(user_id, group_id, messages: list):
        group = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        if group is None:
            return None
        user = Mongo.users.find_one({'user_id': user_id})
        if user is None:
            return None
        if not messages:
            return None
        
        # 更新speakers列表
        for message in messages:
            if not message:
                continue
            speakers_list = group['speakers']
            value = message['speaker_qq']
            index = next((i for i, d in enumerate(speakers_list) if d.get('speaker_qq') == value), None)
            
            if index is not None:
                if message not in group['messages']:
                    speakers_list[index]['speaker_msg_freq'] += 1
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


        
        time_format = "%Y-%m-%d %H:%M:%S"
        existing = group['messages']
        combined = existing + messages
        combined.sort(key=lambda m: datetime.strptime(m['time_str'], time_format))
        seen = set()
        merged_msgs = []
        for msg in combined:
            key = (msg['time_str'], msg['speaker_qq'], msg['content'])
            if key not in seen:
                seen.add(key)
                merged_msgs.append(msg)

        # 更新消息列表和计数
        group['messages'] = merged_msgs
        group['message_num'] = len(merged_msgs)       
        
        #更新时间
        if merged_msgs:
            group['start_time'] = merged_msgs[0]['time_str']
            group['end_time'] = merged_msgs[-1]['time_str']        

        #更新数据库中group
        Mongo.groups.update_one(
            {'user_id': user_id, 'group_id': group_id},
            {'$set': {
                'messages': group['messages'],
                'message_num': group['message_num'],
                'start_time': group['start_time'],
                'end_time': group['end_time'],
                'speakers': group['speakers'],
                'speaker_num': group['speaker_num'],
            }}
        )

        # 返回数据
        return{
            'group_id': group['group_id'],
            'group_name': group.get('group_name'),
            'speaker_num': group['speaker_num'],
            'speaker_list': group['speakers'],
            'start_time': group['start_time'],
            'end_time': group['end_time'],
            'message_num': group['message_num'],
        }
    
    @staticmethod
    def acquire(user_id, group_id, speaker_id) -> list:   #返回类型同传入的messages,发言的前10条和后十条
        group = Mongo.groups.find_one({'user_id': user_id, 'group_id': group_id})
        if group is None:
            return None
        msg_list = group['messages']
        combined = []
        for idx, message in enumerate(msg_list):
            if message['speaker_id'] == speaker_id:
                front_ten = msg_list[max(0, idx-10):idx]
                back_ten = msg_list[idx+1:min(len(msg_list), idx+11)]
                combined += front_ten + [message] + back_ten

        time_format = "%Y-%m-%d %H:%M:%S"
        combined.sort(key=lambda m: datetime.strptime(m['time_str'], time_format))
        seen = set()
        merged_msgs = []
        for msg in combined:
            key = (msg['time_str'], msg['speaker_qq'], msg['content'])
            if key not in seen:
                seen.add(key)
                merged_msgs.append(msg)  
        return merged_msgs      



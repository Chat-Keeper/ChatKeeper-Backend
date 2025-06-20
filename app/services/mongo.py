from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient, ASCENDING

# 1. 建立连接
connecttion_string = "mongodb://172.26.104.63:27017"

client = MongoClient(connecttion_string)
db      = client["ChatKeeper"]
users   = db["users"]
tokens  = db["tokens"]
chats   = db["chats"]
speakers= db["speakers"]

# 对 user_id、token、chat_id 做索引加速查询
users.create_index("user_id", unique=True)
tokens.create_index("token", unique=True)
chats.create_index("chat_id", unique=True)
speakers.create_index([("user_id", ASCENDING), ("name", ASCENDING)], unique=True)

#1. 检查数据库中是否已经存在该用户
def user_exists(username, password):
    user_id = users.find_one({'username': username, 'password': password}, {'user_id': 1})
    if user_id:
        return user_id['user_id']
    else:
        return None


# 2. 创建一个新用户
def create_user(username, password):
    user_id = str(uuid4())
    users.insert_one({
        "user_id": user_id,
        "username": username,
        "password": password,    
        "created_at": datetime.utcnow()
    })
    #生成登录令牌
    token = str(uuid4())
    ttl_minutes = 10  #登录失效时间
    expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
    tokens.insert_one({
        "token": token,
        "user_id": user_id,
        "expires_at": expires_at
    })
    return user_id



# 4. 导入一条聊天记录
def import_chat(user_id, messages):
    """
    messages:  list of dicts, each dict 包含：
       { "speaker": str, "text": str, "timestamp": datetime }
    """
    chat_id = str(uuid4())
    speakers_list = sorted({ msg["speaker"] for msg in messages })
    chats.insert_one({
        "chat_id": chat_id,
        "user_id": user_id,
        "imported_at": datetime.utcnow(),
        "n_messages": len(messages),
        "speakers": speakers_list,
        "messages": messages
    })
    return chat_id



# 6. 更新 speakers 集合
def update_speakers_for_chat(chat_id):
    chat = chats.find_one({"chat_id": chat_id})
    if not chat:
        raise ValueError("找不到对应聊天记录")
    user_id = chat["user_id"]

    # 按发言人分组收集文本
    from collections import defaultdict
    buf = defaultdict(list)
    for msg in chat["messages"]:
        buf[msg["speaker"]].append(msg["text"])

    now = datetime.utcnow()
    for name, texts in buf.items():
        analysis = analyze_personality(texts)
        speakers.update_one(
            {"user_id": user_id, "name": name},
            {
                "$set": {
                    "last_analyzed_at": now,
                    "trait": analysis["trait"],
                    "interest": analysis["interest"]
                }
            },
            upsert=True
        )






from app.utils.utils import check_password_hash, generate_password_hash, create_token, is_strong_password
from app.models.user import User
from app.models.token import Token
from datetime import datetime, timedelta
from flask import current_app
import secrets


class UserService:
    @staticmethod
    def authenticate(username: str, password: str):
        """检查用户名和密码是否正确"""
        user = User.find_name(username)
        if user and check_password_hash(password, user['password']):
            user.pop('password', None)
            return user
        return None

    @staticmethod
    def create_user(username: str, password: str):
        """创建新用户（用于注册功能）"""
        if User.find_name(username):
            return None, 400  # 用户已存在
        if not is_strong_password or len(username) < 5:
            return None, 401  # 非法的用户名或密码
        new_user = {
            'username': username,
            'password': generate_password_hash(password)
        }
        result = User.insert(new_user)
        new_user['user_id'] = result['user_id']
        new_user.pop('password', None)
        return new_user, 200  # 合法返回

    @staticmethod
    def get_token(user_id) -> str:
        token = Token.find_user(user_id)
        if token:
            token = UserService.refresh_token(token)
            return token['token']
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=current_app.config["TTL_MINUTES"])
            token = {
                "token": create_token(),
                "user_id": user_id,
                "expires_at": expires_at
            }
            token = Token.insert(token)
            return token['token']

    @staticmethod
    def refresh_token(token):
        expires_at = datetime.utcnow() + timedelta(minutes=current_app.config["TTL_MINUTES"])
        token = Token.refresh(token['user_id'], expires_at)
        return token

    @staticmethod
    def validate_token(user_id: str, access_token: str) -> bool:
        #"""验证令牌有效性"""
        token = Token.get_token(access_token)
        if token:
            if token['expires_at'] < datetime.utcnow():
                UserService.destroy_token(token['user_id'])
                return False
            return token['user_id'] == user_id


    @staticmethod
    def destroy_token(user_id: str) -> bool:
        return Token.destroy(user_id)

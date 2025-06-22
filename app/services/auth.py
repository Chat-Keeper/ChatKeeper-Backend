from app.services.mongo import User
from app.config import Config
import re
import secrets
class UserService:
    @staticmethod
    def authenticate(username, password):
        """检查用户名和密码是否正确"""
        user=User.user_exists(username)

        if user and check_password_hash(password, user['password']):
            user.pop('password', None)
            return user
        return None



    @staticmethod
    def create_user(username, password):
        """创建新用户（用于注册功能）"""
        if User.user_exists(username):
            return None  # 用户已存在
        #
        new_user = {
            'username': username,
            'password': generate_password_hash(password)
        }
        #
        result = User.user_insert(new_user)
        new_user['user_id'] = result['user_id']
        new_user.pop('password', None)
        return new_user

    @staticmethod
    def create_token() -> str:
        return secrets.token_urlsafe(32)

def generate_password_hash(password: str) -> str:
    return Config.pwd_context.hash(password)


def check_password_hash(password: str, hash: str) -> bool:
    return Config.pwd_context.verify(password, hash)


def is_strong_password(password):
    """检查密码强度"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+=-]", password):
        return False
    return True

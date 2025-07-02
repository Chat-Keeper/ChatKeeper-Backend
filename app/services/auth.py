from app.utils.utils import check_password_hash, generate_password_hash
from app.models.user import User
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

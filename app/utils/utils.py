from app.config import Config
import re
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

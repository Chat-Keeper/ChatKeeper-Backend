from flask import current_app
import secrets
import re


def generate_password_hash(password: str) -> str:
    return current_app.config["PWD_CONTEXT"].hash(password)


def check_password_hash(password: str, hash: str) -> bool:
    return current_app.config["PWD_CONTEXT"].verify(password, hash)


def create_token() -> str:
    return secrets.token_urlsafe(32)


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


def allowed_file(filename):
    """验证文件扩展名"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

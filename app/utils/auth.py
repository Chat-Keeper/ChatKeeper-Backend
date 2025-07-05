from functools import wraps
from flask import request
from app.services.auth_service import UserService


def token_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {
                "code": 401,
                "msg": "Authorization header is missing"
            }, 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return {
                "code": 401,
                "msg": "Authorization header must start with 'Bearer'"
            }, 401

        token = parts[1]
        user_id = UserService.get_user_id(token)
        if not user_id or not UserService.validate_token(user_id, token):
            return {
                "code": 401,
                "msg": "Invalid token"
            }, 401

        return view_func(user_id=user_id, *args, **kwargs)

    return decorated_function

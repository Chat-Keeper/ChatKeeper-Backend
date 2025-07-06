from flask import Blueprint, request
from app.services.auth_service import UserService
from app.utils.auth import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = UserService.authenticate(username, password)
    if user:
        token = UserService.get_token(user["user_id"])
        return {
            "code": 200,
            "msg": username + " Successfully logged in",
            "data": {
                "user_id": user["user_id"],
                "username": username,
                "token": token
            }
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Wrong username or password",
            "data": {}
        }, 400


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(user_id):
    if UserService.destroy_token(user_id):
        return {
            "code": 200,
            "msg": "Successfully logged out",
            "data": {}
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Failed to log out",
            "data": {}
        }, 400


@auth_bp.route('/signup', methods=['POST'])
def signup():
    username = request.json['username']
    password = request.json['password']
    user, error_code = UserService.create_user(username, password)
    if user:
        token = UserService.get_token(user["user_id"])
        return {
            "code": 200,
            "msg": username + " Successfully signed up",
            "data": {
                "user_id": user["user_id"],
                "username": username,
                "token": token
            }
        }, 200
    else:
        if error_code == 400:
            return {
                "code": 400,
                "msg": "username has already been registered",
                "data": {}
            }, 400
        elif error_code == 401:
            return {
                "code": 401,
                "msg": "invalid username or password",
                "data": {}
            }, 401


@auth_bp.route('/verification', methods=['POST'])
@token_required
def verify(user_id):
    return {
        "code": 200,
        "msg": "Valid token",
        "data": {}
    }


@auth_bp.route('/')
def test():
    return "hello world"

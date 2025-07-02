from flask import Blueprint, request
from app.services.auth import UserService
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
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
        }
    else:
        return {
            "code": 400,
            "msg": "Wrong username or password",
        }



@auth_bp.route('/logout', methods=['POST'])
def logout():
    user_id = request.form['user_id']
    token = request.form['token']
    if UserService.destroy_token(user_id):
        return {
            "code": 200,
            "msg": "Successfully logged out",
            "data": {}
        }
    else:
        return {
            "code": 400,
            "msg": "Wrong token",
            "data": {}
        }

@auth_bp.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    user, error_code = UserService.create_user(username, password)
    if user:
        token = UserService.get_token(user["user_id"])
        return {
            "code": 200,
            "msg": username + " Successfully signed up",
            "data": {
                "user_id": user["id"],
                "username": username,
                "token": token
            }
        }
    else:
        if error_code == 400:
            return {
                "code": 400,
                "msg": "user has already been registered",
            }
        if error_code == 401:
            return {
                "code": 401,
                "msg": "invalid username or password",
            }

@auth_bp.route('/')
def test():
    user = {
            "id": "10000000",
            "username": "123456",
            "password": "123456"
        }
    return user

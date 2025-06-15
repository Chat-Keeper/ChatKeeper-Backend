from flask import Blueprint, request

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    return {
        "code": 200,
        "msg": username + ' ' + password + " Successfully logged in",
        "data": {
            "token": "asdfghjkl"
        }
    }


@auth_bp.route('/logout', methods=['POST'])
def logout():
    user_id = request.form['user_id']
    token = request.form['token']
    return {
        "code": 200,
        "msg": user_id + ' ' + token + "Successfully logged out",
        "data": {}
    }


@auth_bp.route('/')
def log():
    return '<h1> Hello </h1>'

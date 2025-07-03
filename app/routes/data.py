from flask import Blueprint, request
from werkzeug.utils import secure_filename
from app.services.auth_service import UserService
from app.services.data_service import DataService
from app.utils.utils import allowed_file
from flask import current_app
import os

# from app.services.auth import UserService


data_bp = Blueprint('data', __name__)


@data_bp.route('/upload', methods=['POST'])
def data_upload():
    user_id = request.form['user_id']
    token = request.form['token']
    group_id = request.form['group_id']
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    if 'chat_log' not in request.files:
        return {
            "code": 400,
            "msg": "No file part"
        }
    chat_log = request.files['chat_log']
    if chat_log.filename == '':
        return {
            "code": 400,
            "msg": "'No selected file'"
        }
    if not allowed_file(chat_log.filename):
        return {
            "code": 400,
            "msg": "Invalid file extension. Only .txt files are allowed"
        }
    file_name = secure_filename(chat_log.filename)

    user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    save_path = os.path.join(user_dir, file_name)
    chat_log.save(save_path)
    return DataService.chat_log_upload(user_id, group_id, save_path)


@data_bp.route('/group/list', methods=['GET'])
def group_list():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    group_list_info = DataService.list_all_group(user_id)
    if group_list_info:
        return {
            "code": 200,
            "msg": "Successfully list all groups.",
            "data": {
                "group_nums": len(group_list_info),
                "group_list": group_list_info
            }
        }
    else:
        return {
            "code": 400,
            "msg": "Can't find any groups."
        }


@data_bp.route('/group/new', methods=['POST'])
def group_new():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    group_name = request.args.get('group_name')
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    result = DataService.create_new_group(user_id, group_name)
    if result:
        return {
            "code": 200,
            "msg": "Successfully create new groups.",
            "data": {}
        }
    else:
        return {
            "code": 400,
            "msg": "Fail to create new groups.",
            "data": {}
        }


@data_bp.route('/group/rename', methods=['POST'])
def group_rename():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    group_id = request.args.get('group_id')
    group_name = request.args.get('group_name')
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    result = DataService.rename_group(user_id, group_id, group_name)
    if result:
        return {
            "code": 200,
            "msg": "Successfully rename the group, new name is" + group_name,
            "data": {}
        }
    else:
        return {
            "code": 400,
            "msg": "Fail to rename the group.",
            "data": {}
        }


@data_bp.route('/speaker/list', methods=['GET'])
def speaker_list():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    speaker_list_info = DataService.list_all_speaker(user_id)
    if speaker_list:
        return {
            "code": 200,
            "msg": "Successfully list all speakers.",
            "data": {
                "speaker_nums": len(speaker_list_info),
                "speaker_info": speaker_list_info
            }
        }
    else:
        return {
            "code": 400,
            "msg": "Can't find any groups.",
            "data": {
                "speaker_nums": len(speaker_list_info),
                "speaker_info": speaker_list_info
            }
        }


@data_bp.route('/speaker/details', methods=['GET'])
def speaker_detail():
    user_id = request.args.get('user_id')
    token = request.args.get('token')
    speaker_id = request.args.get('speaker_id')
    if not UserService.validate_token(user_id, token):
        return {
            "code": 401,
            "msg": "Invalid token"
        }
    speaker_info = DataService.get_speaker_detail(user_id, speaker_id)
    if speaker_info:
        return {
            "code": 200,
            "msg": "Successfully get details of speaker.",
            "data": speaker_info
        }
    else:
        return {
            "code": 400,
            "msg": "Can't get details of speaker.",
            "data": {}
        }

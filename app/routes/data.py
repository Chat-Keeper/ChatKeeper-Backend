from flask import Blueprint, request
from werkzeug.utils import secure_filename
from app.services.data_service import DataService
from app.utils.utils import allowed_file
from app.utils.auth import token_required
from flask import current_app
import os

data_bp = Blueprint('data', __name__)


@data_bp.route('/upload', methods=['POST'])
@token_required
def data_upload(user_id):
    group_id = request.form['group_id']
    if 'chat_log' not in request.files:
        return {
            "code": 402,
            "msg": "No file part",
            "data": {}
        }, 402
    chat_log = request.files['chat_log']
    if chat_log.filename == '':
        return {
            "code": 402,
            "msg": "'No selected file'",
            "data": {}
        }, 402
    if not allowed_file(chat_log.filename):
        return {
            "code": 402,
            "msg": "Invalid file extension. Only .txt files are allowed",
            "data": {}
        }, 402
    file_name = secure_filename(chat_log.filename)

    user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    save_path = os.path.join(user_dir, file_name)
    chat_log.save(save_path)
    try:
        result = DataService.chat_log_upload(user_id, group_id, save_path)
    except ValueError as v:
        return {
            "code": 403,
            "msg": str(v),
            "data": {}
        }, 403
    except RuntimeError as r:
        return {
            "code": 400,
            "msg": str(r),
            "data": {}
        }, 400
    except Exception as e:
        return {
            "code": 404,
            "msg": f"Unknown error:{str(e)}",
            "data": {}
        }, 404
    return {
        "code": 200,
        "msg": "Successfully uploaded data",
        "data": result
    }, 200
@data_bp.route('/group/list', methods=['GET'])
@token_required
def group_list(user_id):
    group_list_info = DataService.list_all_group(user_id)
    if group_list_info:
        return {
            "code": 200,
            "msg": "Successfully list all groups.",
            "data": {
                "group_nums": len(group_list_info),
                "group_list": group_list_info
            }
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Can't find any groups.",
            "data": {}
        }, 400


@data_bp.route('/group/new', methods=['POST'])
@token_required
def group_new(user_id):
    group_name = request.form['group_name']
    group_id = DataService.create_new_group(user_id, group_name)
    if group_id is not None:
        return {
            "code": 200,
            "msg": "Successfully create new groups.",
            "data": {
                "group_id": group_id
            }
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Fail to create new groups.",
            "data": {}
        }, 400


@data_bp.route('/group/rename', methods=['POST'])
@token_required
def group_rename(user_id):
    group_id = request.form['group_id']
    group_name = request.form['group_name']
    result = DataService.rename_group(user_id, group_id, group_name)
    if result:
        return {
            "code": 200,
            "msg": "Successfully rename the group, new name is" + group_name,
            "data": {}
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Fail to rename the group.",
            "data": {}
        }, 400


@data_bp.route('/speaker/list', methods=['GET'])
@token_required
def speaker_list(user_id):
    speaker_list_info = DataService.list_all_speaker(user_id)
    if speaker_list:
        return {
            "code": 200,
            "msg": "Successfully list all speakers.",
            "data": {
                "speaker_nums": len(speaker_list_info),
                "speaker_info": speaker_list_info
            }
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Can't find any groups.",
            "data": {
                "speaker_nums": len(speaker_list_info),
                "speaker_info": speaker_list_info
            }
        }, 400


@data_bp.route('/speaker/details', methods=['GET'])
@token_required
def speaker_detail(user_id):
    speaker_id = request.args.get("speaker_id")
    speaker_info = DataService.get_speaker_detail(user_id, speaker_id)
    if speaker_info:
        return {
            "code": 200,
            "msg": "Successfully get details of speaker.",
            "data": speaker_info
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Can't get details of speaker.",
            "data": {}
        }, 400


@data_bp.route('/group/delete', methods=['POST'])
@token_required
def group_delete(user_id):
    group_id = request.form['group_id']
    if DataService.delete_group(user_id,group_id):
        return {
            "code": 200,
            "msg": "Successfully delete the group",
            "data": {}
        }, 200
    else:
        return {
            "code": 400,
            "msg": "Fail to delete the group.",
            "data": {}
        }, 400
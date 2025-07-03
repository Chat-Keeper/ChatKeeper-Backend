from flask import Blueprint, request
from werkzeug.utils import secure_filename
from app.utils.utils import allowed_file
from flask import current_app
import os
# from app.services.auth import UserService


data_bp = Blueprint('data', __name__)


@data_bp.route('/upload', methods=['POST'])
def upload():
    user_id = request.form['user_id']
    token = request.form['token']
    group_id = request.form['group_id']

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

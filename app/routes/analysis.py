from flask import Blueprint, request
from app.utils.auth import token_required
analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/speaker', methods=['POST'])
@token_required
def speaker(user_id):
    speaker_id = request.form['speaker_id']
    group_id = request.form['group_id']
    try:
        result = DeepseekService.analysis(user_id, group_id, speaker_id)
    except RuntimeError as e:
        return {
            "code": 400,
            "msg": "Failed to get data from database"
        }, 400
    except ConnectionError as c:
        return {
            "code": 405,
            "msg": "Failed to connect to deepseek service"
        }
    except Exception as e:
        return {
            "code": 404,
            "msg": f"Unknown error:{str(e)}"
        }
    return {
        "code": 200,
        "msg": "Successful analyze the speaker",
        "data": result
    }


@analysis_bp.route('/search', methods=['POST'])
@token_required
def search(user_id):
    group_id = request.form['group_id']
    keyword = request.form['keyword']
    try:
        result = DeepseekService.getAssociations(user_id, group_id, keyword)
    except RuntimeError as e:
        return {
            "code": 400,
            "msg": "Failed to get data from database"
        }, 400
    except ConnectionError as c:
        return {
            "code": 405,
            "msg": "Failed to connect to deepseek service"
        }
    except Exception as e:
        return {
            "code": 404,
            "msg": f"Unknown error:{str(e)}",
        }
    return {
        "code": 200,
        "msg": "Successful analyze the speaker",
        "data": result
    }



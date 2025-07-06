from flask import Blueprint, request
from app.utils.auth import token_required
analysis_bp = Blueprint('analysis', __name__)
from app.services.deppseek_service import DeepseekService
from app.models.group import Group
from app.models.speaker import Speaker

@analysis_bp.route('/speaker', methods=['POST'])
@token_required
def speaker(user_id):
    speaker_id = request.form['speaker_id']
    speaker = Speaker.find(user_id, speaker_id)
    #return speaker
    group_id = speaker['group_id']
    try:
        result = DeepseekService.analysis(user_id, group_id, speaker_id)
    except RuntimeError as e:
        return {
            "code": 400,
            "msg": "Failed to get data from database",
            "data": {}
        }, 400
    except ConnectionError as c:
        return {
            "code": 405,
            "msg": "Failed to connect to deepseek service",
            "data": {}
        }
    except Exception as e:
        return {
            "code": 404,
            "msg": f"Unknown error:{str(e)}",
            "data": {}
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
        result = Group.getAssociations(user_id, group_id, keyword)
    except RuntimeError as e:
        return {
            "code": 400,
            "msg": "Failed to get data from database",
            "data": {}
        }, 400
    except ConnectionError as c:
        return {
            "code": 405,
            "msg": "Failed to connect to deepseek service",
            "data": {}
        }
    except Exception as e:
        return {
            "code": 404,
            "msg": f"Unknown error:{str(e)}",
            "data": {}
        }
    return {
        "code": 200,
        "msg": "Successful analyze the speaker",
        "data": result
    }



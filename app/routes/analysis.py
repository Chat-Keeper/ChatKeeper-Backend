from flask import Blueprint, request

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/speaker', methods=['POST'])
def speaker():
    pass


@analysis_bp.route('/search', methods=['POST'])
def search():
    pass


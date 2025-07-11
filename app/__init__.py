import os
from flask import Flask
from app.config import config
from app.models.mongo import Mongo
# from .services.mongo import init_mongo
from flask_cors import CORS

from app.routes.data import data_bp
from app.routes.auth import auth_bp
from app.routes.analysis import analysis_bp
import json
from bson import ObjectId
from flask import Flask


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


def create_app(config_name="development"):
    app = Flask(__name__)

    # 允许跨域访问
    CORS(app)

    app.json_encoder = MongoJSONEncoder
    # 导入配置
    app.config.from_object(config[config_name])

    # 初始化MongoDB
    Mongo.init_mongo(app)  # 调用User类中的方法

    # 注册蓝图
    register_blueprints(app)

    return app


def register_blueprints(app):
    """注册所有蓝图到应用"""
    # 注册蓝图并指定URL前缀
    # app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    #analysis_bp = Blueprint('analysis', __name__)


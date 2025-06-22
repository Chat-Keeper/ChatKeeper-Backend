import os
from flask import Flask
from .config import config
from app.services.mongo import User
# from .services.mongo import init_mongo

# from .routes.analysis import analysis_bp
from .routes.auth import auth_bp

def create_app(config_name="development"):
    app = Flask(__name__)

    # 导入配置
    app.config.from_object(config[config_name])

    # 初始化MongoDB
    User.init_mongo(app)   #调用User类中的方法

    # 注册蓝图
    register_blueprints(app)

    return app


def register_blueprints(app):
    """注册所有蓝图到应用"""
    # 注册蓝图并指定URL前缀
    #app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(auth_bp, url_prefix='/auth')



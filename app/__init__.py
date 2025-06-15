import os
from flask import Flask
from .config import config


def create_app(config_name="development"):
    app = Flask(__name__)

    # 导入配置
    app.config.from_object(config[config_name])

    # 注册蓝图
    register_blueprints(app)

    return app


def register_blueprints(app):
    """注册所有蓝图到应用"""
    # 从路由模块导入蓝图
    #from .routes.analysis import analysis_bp
    from .routes.auth import auth_bp

    # 注册蓝图并指定URL前缀
    #app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(auth_bp, url_prefix='/auth')
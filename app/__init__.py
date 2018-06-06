import os

from flask import Flask

from app.config import ProductConfig, DevConfig
from app.models import db, User
from app.views.urls import api


def create_app():
    app = Flask(__name__)

    # 根据环境变量加载开发环境或生产环境配置
    env = os.environ.get('RM_ENV')

    if env in ('pro', 'prod', 'product'):
        app.config.from_object(ProductConfig)
    else:
        app.config.from_object(DevConfig)

    # 从环境变量 RMON_SETTINGS 指定的文件中加载配置
    app.config.from_envvar('RM_SETTINGS', silent=True)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 注册 Blueprint
    app.register_blueprint(api)
    # 初始化数据库
    db.init_app(app)
    # 如果是开发环境则创建所有数据库表
    if app.debug:
        with app.app_context():
            db.create_all()
            name, password = User.create_administrator()
    return app



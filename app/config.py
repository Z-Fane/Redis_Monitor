import os

class DevConfig:
    """开发环境配置
    """
    SECRET_KEY ='OQR!YuiIZ0K5!NmqI1zy@S7x&ac5zJ9DAQhb'

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # sqlite 数据库文件路径
    path = os.path.join(os.getcwd(), 'rmon.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % path
    TEMPLATES_AUTO_RELOAD = True
    WX_TOKEN='hellozfane'
    WX_APP_ID='wx512fda512d5458b3'
    WX_SECRET='c94760e8e991868306378b5130a43583'


class ProductConfig(DevConfig):
    """生产环境配置
    """
    DEBUG = False
    # sqlite 数据库文件路径
    path = os.path.join(os.getcwd(), 'rmon.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % path

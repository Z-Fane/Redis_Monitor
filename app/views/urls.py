
from flask import Blueprint

from app.views.views import IndexView, ServerList, ServerDetail, ServerMetrics, AuthView, UserDetail, UserList
from app.wx.wx import WxView, WxBind

api = Blueprint('api', __name__)

# 首页
api.add_url_rule('/', view_func=IndexView.as_view('index'))

# 登录
api.add_url_rule('/login', view_func=AuthView.as_view('login'))

# 用户管理
api.add_url_rule('/users/', view_func=UserList.as_view('user_list'))
api.add_url_rule('/users/<int:object_id>',
                 view_func=UserDetail.as_view('user_detail'))

# Redis 服务器管理
api.add_url_rule('/servers/',
                 view_func=ServerList.as_view('server_list'))
api.add_url_rule('/servers/<int:object_id>',
                 view_func=ServerDetail.as_view('server_detail'))
api.add_url_rule('/servers/<int:object_id>/metrics',
                 view_func=ServerMetrics.as_view('server_metrics'))


# # 微信接口
api.add_url_rule('/wx/', view_func=WxView.as_view('wx_view'))
api.add_url_rule('/wx/bind/<wx_id>', view_func=WxBind.as_view('wx_bind'))

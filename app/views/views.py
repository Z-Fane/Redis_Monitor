from flask import render_template, request
from flask.views import MethodView

from app.common.rest import RestView
from app.models import Server, ServerSchema


class IndexView(MethodView):
    """首页视图
    """

    def get(self):
        """渲染模板
        """
        return render_template('index.html')

class ServerList(RestView):
    """Redis 服务器列表
    """
    def get(self):
        servers = Server.query.all()
        return ServerSchema().dump(servers, many=True).data

    def post(self):
        """创建 Redis 实例
        """
        data = request.get_json()
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        return {'ok': True}, 201


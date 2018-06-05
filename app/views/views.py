from flask import render_template, request, g
from flask.views import MethodView

from app.common.rest import RestView
from app.models import Server, ServerSchema
from app.views.decorators import ObjectMustBeExist


class IndexView(MethodView):
    """首页视图
    """

    def get(self):
        """渲染模板
        """
        return render_template('index.html')

class ServerList(RestView):
    def get(self):
        servers = Server.query.all()
        return ServerSchema().dump(servers, many=True).data

    def post(self):
        data = request.get_json()
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        return {'ok': True}, 201
class ServerDetail(RestView):
    """ Redis 服务器列表
    """
    method_decorators = (ObjectMustBeExist(Server), )

    def get(self, object_id):
        data, _ = ServerSchema().dump(g.instance)
        return data

    def put(self, object_id):
        schema = ServerSchema(context={'instance': g.instance})
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        a=g
        g.instance.delete()
        return {'ok': True}, 204
class  ServerMetrics(RestView):
    method_decorators = (ObjectMustBeExist(Server),)
    def get(self,object_id):
        return g.instance.get_metrics()



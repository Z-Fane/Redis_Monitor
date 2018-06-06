from datetime import datetime

from flask import render_template, request, g
from flask.views import MethodView

from app.common.errors import RestError, AuthenticateError
from app.common.rest import RestView
from app.models import Server, ServerSchema, User, UserSchema
from app.views.decorators import ObjectMustBeExist, TokenAuthenticate


class IndexView(MethodView):
    def get(self):

        return render_template('index.html')

class ServerList(RestView):
    method_decorators = (TokenAuthenticate(), )
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
    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(Server))

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
        '''
        为什么通过g就能拿到object_id对应的数据呢？
        因为装饰器。
        :param object_id:
        :return:
        '''
        g.instance.delete()
        return {'ok': True}, 204
class  ServerMetrics(RestView):
    method_decorators = (ObjectMustBeExist(Server),TokenAuthenticate())
    def get(self,object_id):
        return g.instance.get_metrics()

class AuthView(RestView):
    def post(self):
        # FIXME 没有处理 data 为 None 的情况
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')

        if not name or not password:
            raise AuthenticateError(403, 'user name or password required')

        # FIXME 只有管理员用户允许登录管理后台
        user = User.authenticate(name, password)
        user.login_at = datetime.utcnow()
        user.save()
        return {'ok': True, 'token': user.generate_token()}

class UserList(RestView):
    """Redis 服务器列表
    """

    method_decorators = (TokenAuthenticate(), )

    def get(self):
        """获取 Redis 列表
        """
        servers = User.query.all()
        return UserSchema().dump(servers, many=True).data

    def post(self):
        """创建 Redis 实例
        """
        data = request.get_json()
        user, errors = UserSchema().load(data)
        if errors:
            return errors, 400
        user.save()
        return {'ok': True}, 201
class UserDetail(RestView):
    """ Redis 服务器列表
    """
    method_decorators = (TokenAuthenticate(), ObjectMustBeExist(User))

    def get(self, object_id):
        """
        """
        data, _ = UserSchema().dump(g.instance)
        return data

    def put(self, object_id):
        """更新服务器
        """
        schema = UserSchema(context={'instance': g.instance})
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除服务器
        """
        # 删除服务器时候需要判断当时是否还有没有管理员账户
        if User.query.filter(User.id!=g.instance.id).count() == 0:
            raise RestError(400, 'must have one administrator')

        g.instance.delete()
        return {'ok': True}, 204




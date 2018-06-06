from collections import Mapping

from flask import Response, make_response, request
from flask.json import dumps
from flask.views import MethodView


# 自定义View:json 序列化，异常处理，装饰器支持
from app.common.errors import RestError


class RestView(MethodView):
    content_type = 'application/json; charset=utf-8'
    method_decorators = []
    #处理异常
    def handler_error(self, exception):
        data = {
            'ok': False,
            'message': exception.message
        }
        result = dumps(data) + '\n'
        resp = make_response(result, exception.code)
        resp.headers['Content-Type'] = self.content_type
        return resp
    #支持数据自动序列化
    def dispatch_request(self, *args, **kwargs):
        # 获取对应于 HTTP 请求方式的方法
        method = getattr(self, request.method.lower(), None)
        if method is None and request.method == 'HEAD':
            method = getattr(self, 'get', None)
        assert method is not None, 'Unimplemented method %r' % request.method
        # HTTP请求方法定义了不同的装饰器
        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            method = decorator(method)
        try:
            resp = method(*args, **kwargs)
        except RestError as e:
            resp = self.handler_error(e)
        # 如果返回结果已经是 HTTP 响应则直接返回
        if isinstance(resp, Response):
            return resp
        # 从返回值中解析出 HTTP 响应信息，比如状态码和头部
        data, code, headers = RestView.unpack(resp)
        # 处理错误，HTTP 状态码大于 400 时认为是错误
        # 返回的错误类似于 {'name': ['redis server already exist']} 将其调整为
        # {'ok': False, 'message': 'redis server already exist'}
        if code >= 400 and isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list) and len(data[key]) > 0:
                    message = data[key][0]
                else:
                    message = data[key]
            data = {'ok': False, 'message': message}

        # 序列化数据
        result = dumps(data) + '\n'
        # 生成 HTTP 响应
        response = make_response(result, code)
        response.headers.extend(headers)

        # 设置响应头部为 applicaiton/json
        response.headers['Content-Type'] = self.content_type
        return response

    @staticmethod
    def unpack(value):
        """解析视图方法返回值
        """
        headers = {}
        if not isinstance(value, tuple):
            return value, 200, {}
        # 如果返回值有 3
        if len(value) == 3:
            data, code, headers = value
        elif len(value) == 2:
            data, code = value
        return data, code, headers

from functools import wraps

from flask import g, request

from app.common.errors import AuthenticateError
from app.common.rest import RestError
from app.models import User


class ObjectMustBeExist():
    def __init__(self,object_class):
        self.object_class=object_class

    def __call__(self,func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            object_id=kwargs['object_id']
            if object_id is None:
                raise RestError(404, 'object not exist')
            obj=self.object_class.query.get(object_id)
            if obj is None:
                raise RestError(404, 'object not exist')
            g.instance=obj
            return func(*args,**kwargs)
        return wrapper
class TokenAuthenticate():
    """通过 jwt 认证用户

    验证 HTTP Authorization 头所包含的 token
    """

    def __init__(self, admin=True):
        """
        Args:
            admin(bool): 是否需要验证管理员权限
        """
        self.admin = admin

    def __call__(self, func):
        """装饰器实现
        """
        @wraps(func)
        def wrapper(*args, **kwargs):

            pack = request.headers.get('Authorization', None)
            if pack is None:
                raise AuthenticateError(401, 'token not found')
            parts = pack.split()
            # Authorization 头部值必须为 'jwt <token_value>' 这种形式
            if parts[0].lower() != 'jwt':
                raise AuthenticateError(401, 'invalid token header')
            elif len(parts) == 1:
                raise AuthenticateError(401, 'token missing')
            elif len(parts) > 2:
                raise AuthenticateError(401, 'invalid token')
            token = parts[1]
            user = User.verify_token(token)

            # 如果需要验证是否是管理员
            if self.admin and not user.is_admin:
                raise AuthenticateError(403, 'no permission')

            # 将当前用户存入到 g 对象中
            g.user = user
            return func(*args, **kwargs)
        return wrapper





class RestError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(RestError, self).__init__()
#redis链接错误
class RedisConnectError(RestError):
    pass
# 用户验证错误
class AuthenticateError(RestError):
    pass
# Token错误
class InvalidTokenError(RestError):
    pass

class RestException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(RestException, self).__init__()
class AuthenticationError(Exception):
    pass
class InvalidTokenError(Exception):
    pass
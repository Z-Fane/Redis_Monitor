from functools import wraps

from flask import g

from app.common.rest import RestException


class ObjectMustBeExist():
    def __init__(self,object_class):
        self.object_class=object_class

    def __call__(self,func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            object_id=kwargs['object_id']
            if object_id is None:
                raise RestException(404,'object not exist')
            obj=self.object_class.query.get(object_id)
            if obj is None:
                raise RestException(404,'object not exist')
            g.instance=obj
            return func(*args,**kwargs)
        return wrapper
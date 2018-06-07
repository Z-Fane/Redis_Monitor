from wechatpy import create_reply
from wechatpy.events import SubscribeEvent

# 消息处理器
from wechatpy.messages import TextMessage


class BaseHandler():
    def __init__(self,wx_client):
        self.wx_client=wx_client
    def handle(self,message,*args,**kwargs):
        raise NotImplementedError('must be implement')

class SubscribeEventHandler(BaseHandler):
    def handle(self,message,*args,**kwargs):
        if not isinstance(message,SubscribeEvent):
            return
        # result=self.wx_client.user.get(message.source)
        return create_reply('欢迎关注ZFane',message)
class  EchoHandler(BaseHandler):
    def handle(self, message, *args, **kwargs):
        if not isinstance(message, TextMessage):
            return
        return create_reply(message.content, message)

default_handlers = (SubscribeEventHandler,EchoHandler)

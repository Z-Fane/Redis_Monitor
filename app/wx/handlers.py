from flask import url_for
from wechatpy import create_reply
from wechatpy.events import SubscribeEvent

# 消息处理器
from wechatpy.messages import TextMessage

from app import User


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
class CommandHandler(BaseHandler):
    command=''
    def check_match(self,message):
        if not isinstance(message,TextMessage):
            return False
        if not message.content.strip().lower().startswith(self.command):
            return False
        return True
class BindCommandHandler(CommandHandler):
    command = 'bind'
    def handle(self,message):
        if not self.check_match(message):
            return
        user=User.wx_id_user(message.source)
        if user is not None:
            return create_reply('你已绑定到 %s 用户' % user.name, message)
        url=url_for('api.wx_bind',wx_id=message.source,_external=True)
        return create_reply('请打开%s链接，完成绑定'%url,message)

default_handlers = (SubscribeEventHandler,BindCommandHandler)

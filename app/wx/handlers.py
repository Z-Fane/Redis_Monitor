from flask import url_for
from wechatpy import create_reply
from wechatpy.events import SubscribeEvent

# 消息处理器
from wechatpy.messages import TextMessage

from app import User
from app.models import Server


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
class RedisCommandHandler(CommandHandler):
    command = 'redis'
    def handle(self,message):
        # 检查命令
        if not self.check_match(message):
            return
        # 检查绑定
        user=User.wx_id_user(wx_id=message.source)
        if user is None:
            return create_reply('您还未绑定，请先绑定', message)
        parts = message.content.strip().split(' ')
        if len(parts) == 1:
            return create_reply('请输入子命令', message)
        if parts[1].lower() == 'ls':
            return create_reply(self.list_servers(), message)
        elif parts[1].lower() == 'del':
            return create_reply(self.delete_server(*parts[2:]), message)
        else:
            return create_reply('命令暂未实现', message)
    def list_servers(self):
        content = ''
        for server in Server.query:
            item = '%s %s %s\n' % (server.name, server.host, server.status)
            content += item
        if not content:
            return '还未创建任何 Redis 服务器'
        return content
    def delete_server(self,*servers):
        if len(servers)==0:
            return '未指定redis服务器名称'
        result = ''
        for name in servers:
            server = Server.query.filter_by(name=name).first()
            if server:
                server.delete()
                result += '成功删除 %s\n' % server.name
            else:
                result += '未发现 %s\n'
        return result



default_handlers = (SubscribeEventHandler,BindCommandHandler,RedisCommandHandler)

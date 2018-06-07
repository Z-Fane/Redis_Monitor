import hashlib

from flask import request, abort, current_app, render_template, make_response
from flask.views import MethodView
from wechatpy import parse_message

from app import User
from app.common.rest import RestView
from app.wx import wx_dispatcher


class WxView(MethodView):
    def check_signature(self):
        signature=request.args.get('signature')
        if signature is None:
            abort(403)
        nonce=request.args.get('nonce')
        timestamp=request.args.get('timestamp')
        msg=[current_app.config['WX_TOKEN'],timestamp,nonce]
        msg.sort()
        sha = hashlib.sha1()
        sha.update(''.join(msg).encode('utf-8'))
        if sha.hexdigest()!=signature:
            abort(403)
    def get(self):
        self.check_signature()
        return request.args.get('echostr')
    def post(self):
        self.check_signature()
        msg=parse_message(request.data)
        reply=wx_dispatcher.dispatch(msg)
        return reply.render()
class WxBind(RestView):
    def get(self,wx_id):
        result=render_template('wx_bind.html')
        return make_response(result,200)
    def post(self,wx_id):
        data=request.get_json()
        if data is None or 'name' not in data or 'password' not in data:
            return {'ok':False,'message':'无效用户数据'}
        user=User.authenticate(data['name'],data['password'])
        if user.wx_id is not None:
            return {'ok':False,'message':'已绑定到其他微信账号'}
        user.wx_id=wx_id
        user.save()
        return {'ok':True,'message':'绑定成功'}

import hashlib

from flask import request, abort, current_app
from flask.views import MethodView
from wechatpy import parse_message

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
from calendar import timegm

import jwt
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from jwt import InvalidTokenError
from marshmallow import post_load, ValidationError, validates_schema, fields, validate, Schema
from redis import RedisError, StrictRedis
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from app.common.errors import RedisConnectError, AuthenticateError
from app.common.rest import RestError

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Server(BaseModel):
    __tablename__ = 'redis_server'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    host = db.Column(db.String(15))
    port = db.Column(db.Integer, default=6379)
    password = db.Column(db.String())

    @property
    def status(self):
        status = 'error'
        try:
            if self.ping():
                status = 'ok'
        except RedisError:
            raise RestError(400, 'redis server %s can not connected' % self.host)
        return status

    def ping(self):
        try:
            return self.redis.ping()
        except RedisConnectError:
            raise RedisConnectError(400, 'redis server %s can not connected' % self.host)

    def get_metrics(self):
        try:
            return self.redis.info()
        except RedisConnectError:
            raise RedisConnectError(400, 'redis server %s can not connected' % self.host)

    @property
    def redis(self):
        return StrictRedis(host=self.host, port=self.port, password=self.password)


class ServerSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    description = fields.String(validate=validate.Length(0, 512))
    # host 必须是 IP v4 地址，通过正则验证
    host = fields.String(required=True,
                         validate=validate.Regexp(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'))
    port = fields.Integer(validate=validate.Range(1024, 65536))
    password = fields.String()
    updated_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data):
        """验证是否已经存在同名 Redis 服务器
        """
        if 'port' not in data:
            data['port'] = 6379

        instance = self.context.get('instance', None)

        server = Server.query.filter_by(name=data['name']).first()

        if server is None:
            return

        # 更新服务器时
        if instance is not None and server != instance:
            raise ValidationError('Redis server already exist', 'name')

        # 创建服务器时
        if instance is None and server:
            raise ValidationError('Redis server already exist', 'name')

    @post_load
    def create_or_update(self, data):
        """数据加载成功后自动创建 Server 对象
        """
        instance = self.context.get('instance', None)

        # 创建 Redis 服务器
        if instance is None:
            return Server(**data)

        # 更新服务器
        for key in data:
            setattr(instance, key, data[key])
        return instance


class User(BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    # 用户微信 ID，全局唯一
    wx_id = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    login_at = db.Column(db.DateTime)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, passwd):
        self._password = generate_password_hash(passwd)

    def verify_password(self, password):
        return check_password_hash(self.password,password)

    @classmethod
    def authenticate(cls, identifier, password):
        user = cls.query.filter(db.or_(cls.name == identifier,
                                       cls.email == identifier)).first()
        if user is None or not user.verify_password(password):
            raise AuthenticateError(403, 'authentication failed')
        return user

    def generate_token(self):
        # 过期时间
        exp = datetime.utcnow() + timedelta(days=1)
        # 过期后10分钟内，还可以通过老Token获取新Token
        refresh_exp = timegm((exp + timedelta(seconds=60 * 10)).utctimetuple())
        payload = {
            'uid': self.id,
            'is_admin': self.is_admin,
            'exp': exp,
            'refresh_exp': refresh_exp
        }
        return jwt.encode(payload, current_app.secret_key, algorithm='HS512').decode('utf-8')

    @classmethod
    def verify_token(cls, token, verify_exp=True):
        if verify_exp:
            options = None
        else:
            options = {'verify_exp': False}
        try:
            payload = jwt.decode(token, current_app.secret_key,verify=True, algorithms=['HS512'], options=options, require_exp=True)
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(403, str(e))
        if any(('is_admin' not in payload,
                'refresh_exp' not in payload, 'uid' not in payload)):
            raise InvalidTokenError(403, 'invalid token')
        # 如果刷新时间过期，则认为 token 无效
        if payload['refresh_exp'] < timegm(datetime.utcnow().utctimetuple()):
            raise InvalidTokenError(403, 'invalid token')
        u = User.query.get(payload.get('uid'))
        if u is None:
            raise InvalidTokenError(403, 'user not exist')
        return u

    @classmethod
    def create_administrator(cls):
        name = 'admin'
        # 管理员账户名称默认为 admin
        admin = cls.query.filter_by(name=name).first()
        if admin:
            return admin.name, ''
        password = '123456'
        admin = User(name=name, email='amin@zfane.cn', is_admin=True)
        admin.password = password
        admin.save()
        return name, password

    @classmethod
    def wx_id_user(cls, wx_id):
        return cls.query.filter_by(wx_id=wx_id).first()


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    email = fields.Email(required=True, validate=validate.Length(2, 64))
    password = fields.String(load_only=True, validate=validate.Length(2, 128))
    is_admin = fields.Boolean()
    wx_id = fields.String(dump_only=True)
    login_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data):
        instance = self.context.get('instance', None)

        user = User.query.filter(db.or_(User.name == data.get('name'),
                                        User.email == data.get('email'))).first()

        if user is None:
            return

        # 创建服务器时
        if instance is None:
            field = 'name' if user.name == data['name'] else 'email'
            raise ValidationError('user already exist', field)

        # 更新用户时
        if user != instance:
            # 判断是存在同名用户或者是同邮箱的用户
            field = 'name' if user.name == instance.name else 'email'
            raise ValidationError('user already exist', field)

    @post_load
    def create_or_update(self, data):
        """数据加载成功后自动创建 User
        """
        instance = self.context.get('instance', None)

        # 创建用户
        if instance is None:
            user = User()
        # 更新用户
        else:
            user = instance

        # FIXME 更新用户时可能覆盖用户密码
        for key in data:
            setattr(user, key, data[key])
        return user

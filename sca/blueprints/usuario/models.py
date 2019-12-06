import datetime
from collections import OrderedDict
from hashlib import md5

import pytz
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer
from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from sca.extensions import db


class Usuario(UserMixin, ResourceMixin, db.Model):
    ROLE = OrderedDict([
        ('basico', 'Basico'),
        ('admin', 'Administrador')
    ])

    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)

    # Authentication.
    perfil = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False), index=True, nullable=False, server_default='basico')
    ativo = db.Column(db.Boolean(), nullable=False, server_default='1')
    nome = db.Column(db.String(24), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False, server_default='')
    senha = db.Column(db.String(128), nullable=False, server_default='')

    # Activity tracking.
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Usuario, self).__init__(**kwargs)

        self.password = Usuario.encrypt_password(kwargs.get('senha', ''))

    @classmethod
    def find_by_identity(cls, identity):

        return Usuario.query.filter((Usuario.email == identity) | (Usuario.nome == identity)).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):

        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    @classmethod
    def deserialize_token(cls, token):
        
        private_key = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        
        try:
            decoded_payload = private_key.loads(token)
            return Usuario.find_by_identity(decoded_payload.get('usuario_email'))

        except Exception:
            return None

    @classmethod
    def initialize_password_reset(cls, identity):

        u = Usuario.find_by_identity(identity)
        reset_token = u.serialize_token()

        # This prevents circular imports.
        from sca.blueprints.user.tasks import (deliver_password_reset_email)
        deliver_password_reset_email.delay(u.id, reset_token)

        return u

    def is_active(self):

        return self.active

    def get_auth_token(self):
       
        private_key = current_app.config['SECRET_KEY']

        serializer = URLSafeTimedSerializer(private_key)
        data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

        return serializer.dumps(data)

    def authenticated(self, with_password=True, password=''):
       
        if with_password:
            return check_password_hash(self.password, password)

        return True

    def serialize_token(self, expiration=3600):
        
        private_key = current_app.config['SECRET_KEY']

        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        return serializer.dumps({'usuario_email': self.email}).decode('utf-8')

    def update_activity_tracking(self, ip_address):
       
        self.sign_in_count += 1

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()

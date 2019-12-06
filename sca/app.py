from flask import Flask
from celery import Celery

from sca.blueprints.page import page
from sca.blueprints.contato import contato
from sca.blueprints.usuario import usuario
from sca.blueprints.usuario.models import Usuario

from sca.extensions import debug_toolbar, mail, csrf, db, login_manager


CELERY_TASK_LIST = [
    'sca.blueprints.contato.tasks',
    'sca.blueprints.usuario.tasks',
]


def create_celery_app(app=None):

    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'], include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(page)
    app.register_blueprint(contato)
    app.register_blueprint(usuario)
    extensions(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    return app


def extensions(app):

    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    return None

def authentication(app, user_model):

    login_manager.login_view = 'usuario.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)

    @login_manager.token_loader
    def load_token(token):
        duration = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=duration)
        user_uid = data[0]

        return user_model.query.get(user_uid)
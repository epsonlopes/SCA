from flask import Flask
from celery import Celery

from sca.blueprints.page import page
from sca.blueprints.contato import contato
from sca.extensions import debug_toolbar, mail, csrf


CELERY_TASK_LIST = [
    'sca.blueprints.contato.tasks',
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
    extensions(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    return app


def extensions(app):

    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    return None
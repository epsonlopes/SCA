from datetime import timedelta

DEBUG = True

SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'chaveinseguraparadesenvolvimento'

# Flask-Mail.
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'awesomepassword'

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5

# SQLAlchemy.
db_uri = 'postgresql://sca:m@ster@postgres:5432/sca'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Usuario.
SEED_ADMIN_EMAIL = 'sca@local.host'
SEED_ADMIN_SENHA = 'm@ster01020304'
REMEMBER_COOKIE_DURATION = timedelta(days=90)
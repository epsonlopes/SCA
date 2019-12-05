from lib.flask_mailplus import send_template_message
from sca.app import create_celery_app

celery = create_celery_app()


@celery.task()
def deliver_contact_email(email, message):

    ctx = {'email': email, 'message': message}

    send_template_message(subject='S.C.A. Contato',
                          sender=email,
                          recipients=[celery.conf.get('MAIL_USERNAME')],
                          reply_to=email,
                          template='contato/mail/index', ctx=ctx)

    return None
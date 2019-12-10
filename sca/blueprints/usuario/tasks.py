from lib.flask_mailplus import send_template_message
from sca.app import create_celery_app
from sca.blueprints.usuario.models import Usuario

celery = create_celery_app()


@celery.task()
def deliver_password_reset_email(user_id, reset_token):
    """
    Send a reset password e-mail to a user.

    :param user_id: The user id
    :type user_id: int
    :param reset_token: The reset token
    :type reset_token: str
    :return: None if a user was not found
    """
    usuario = Usuario.query.get(user_id)

    if usuario is None:
        return

    ctx = {'usuario': usuario, 'reset_token': reset_token}

    send_template_message(subject='Recuperacao de senha do S.C.A.', recipients=[usuario.email], template='usuario/mail/password_reset', ctx=ctx)

    return None

from wtforms.validators import ValidationError
from sca.blueprints.usuario.models import Usuario


def ensure_identity_exists(form, field):
    """
    Ensure an identity exists.

    :param form: wtforms Instance
    :param field: Field being passed in
    :return: None
    """
    usuario = Usuario.find_by_identity(field.data)

    if not usuario:
        raise ValidationError('Unable to locate account.')


def ensure_existing_password_matches(form, field):
    """
    Ensure that the current password matches their existing password.

    :param form: wtforms Instance
    :param field: Field being passed in
    :return: None
    """
    usuario = Usuario.query.get(form._obj.id)

    if not usuario.authenticated(password=field.data):
        raise ValidationError('Does not match.')

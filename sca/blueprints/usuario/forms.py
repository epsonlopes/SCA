from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Email, Unique

from lib.util_wtforms import ModelForm
from sca.blueprints.usuario.models import Usuario, db
from sca.blueprints.usuario.validations import ensure_identity_exists, ensure_existing_password_matches


class LoginForm(Form):
    next = HiddenField()
    identity = StringField('Usuario ou e-mail', [DataRequired(), Length(3, 254)])
    senha = PasswordField('Senha', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class BeginPasswordResetForm(Form):
    identity = StringField('Usuario ou e-mail', [DataRequired(), Length(3, 254), ensure_identity_exists])


class PasswordResetForm(Form):
    reset_token = HiddenField()
    senha = PasswordField('Senha', [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            Usuario.email,
            get_session=lambda: db.session
        )
    ])
    senha = PasswordField('Senha', [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    nome = StringField(validators=[
        Unique(
            Usuario.nome,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Senha atual',
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = EmailField(validators=[
        Email(),
        Unique(
            Usuario.email,
            get_session=lambda: db.session
        )
    ])
    senha = PasswordField('Senha', [Optional(), Length(8, 128)])

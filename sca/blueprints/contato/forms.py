from flask_wtf import Form
from wtforms import TextAreaField
from wtforms_components import EmailField
from wtforms.validators import DataRequired, Length


class ContatoForm(Form):
    email = EmailField("Qual o seu endereco de e-mail?", [DataRequired(), Length(3, 254)])
    message = TextAreaField("Qual seu problema ou duvida?", [DataRequired(), Length(1, 8192)])

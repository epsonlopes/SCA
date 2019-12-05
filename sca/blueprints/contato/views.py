from flask import (Blueprint, flash, redirect, request, url_for, render_template)
from sca.blueprints.contato.forms import ContatoForm

contato = Blueprint('contato', __name__, template_folder='templates')


@contato.route('/contato', methods=['GET', 'POST'])
def index():
    form = ContatoForm()

    if form.validate_on_submit():
        # This prevents circular imports.
        from sca.blueprints.contato.tasks import deliver_contact_email

        deliver_contact_email.delay(request.form.get('email'), request.form.get('message'))

        flash('Obrigado, entraremos em contato o mais rapido possivel.', 'success')
        return redirect(url_for('contato.index'))

    return render_template('contato/index.html', form=form)

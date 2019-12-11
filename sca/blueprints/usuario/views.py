from flask import Blueprint, redirect, request, flash, url_for, render_template
from flask_login import login_required, login_user, current_user, logout_user
from lib.safe_next_url import safe_next_url
from sca.blueprints.usuario.decorators import anonymous_required
from sca.blueprints.usuario.models import Usuario
from sca.blueprints.usuario.forms import LoginForm, BeginPasswordResetForm, PasswordResetForm, SignupForm, WelcomeForm, UpdateCredentials


usuario = Blueprint('usuario', __name__, template_folder='templates')


@usuario.route('/login', methods=['GET', 'POST'])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get('next'))

    if form.validate_on_submit():
        u = Usuario.find_by_identity(request.form.get('identity'))

        if u and u.authenticated(senha=request.form.get('senha')):
            # As you can see remember me is always enabled, this was a design
            # decision I made because more often than not users want this
            # enabled. This allows for a less complicated login form.
            #
            # If however you want them to be able to select whether or not they
            # should remain logged in then perform the following 3 steps:
            # 1) Replace 'True' below with: request.form.get('remember', False)
            # 2) Uncomment the 'remember' field in user/forms.py#LoginForm
            # 3) Add a checkbox to the login form with the id/name 'remember'
            if login_user(u, remember=True) and u.ativo():
                u.update_activity_tracking(request.remote_addr)

                # Handle optionally redirecting to the next URL safely.
                next_url = request.form.get('next')
                if next_url:
                    return redirect(safe_next_url(next_url))

                return redirect(url_for('usuario.settings'))
            else:
                flash('Esse usuario foi desabilitado.', 'error')
        else:
            flash('E-mail ou senha invalidos.', 'error')

    return render_template('usuario/login.html', form=form)


@usuario.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('usuario.login'))


@usuario.route('/account/begin_password_reset', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = Usuario.initialize_password_reset(request.form.get('identity'))

        flash('An email has been sent to {0}.'.format(u.email), 'success')
        return redirect(url_for('usuario.login'))

    return render_template('usuario/begin_password_reset.html', form=form)


@usuario.route('/account/password_reset', methods=['GET', 'POST'])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = Usuario.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash('Your reset token has expired or was tampered with.',
                  'error')
            return redirect(url_for('user.begin_password_reset'))

        form.populate_obj(u)
        u.senha = Usuario.encrypt_password(request.form.get('senha'))
        u.save()

        if login_user(u):
            flash('Sua senha foi redefinida.', 'success')
            return redirect(url_for('usuario.settings'))

    return render_template('usuario/password_reset.html', form=form)


@usuario.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        u = Usuario()

        form.populate_obj(u)
        u.senha = Usuario.encrypt_password(request.form.get('senha'))
        u.save()

        if login_user(u):
            flash('Isso ai!, obrigado por se registrar!', 'success')
            return redirect(url_for('usuario.welcome'))

    return render_template('usuario/signup.html', form=form)


@usuario.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    if current_user.username:
        flash('You already picked a username.', 'warning')
        return redirect(url_for('usuario.settings'))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('nome')
        current_user.save()

        flash('Sign up is complete, enjoy our services.', 'success')
        return redirect(url_for('usuario.settings'))

    return render_template('usuario/welcome.html', form=form)


@usuario.route('/settings')
@login_required
def settings():
    return render_template('usuario/settings.html')


@usuario.route('/settings/update_credentials', methods=['GET', 'POST'])
@login_required
def update_credentials():
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        new_password = request.form.get('senha', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.senha = Usuario.encrypt_password(new_password)

        current_user.save()

        flash('Your sign in settings have been updated.', 'success')
        return redirect(url_for('usuario.settings'))

    return render_template('usuario/update_credentials.html', form=form)

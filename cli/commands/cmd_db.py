import click
from sqlalchemy_utils import database_exists, create_database
from sca.app import create_app
from sca.extensions import db
from sca.blueprints.usuario.models import Usuario

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False, help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()
    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)

    return None


@click.command()
def seed():

    if Usuario.find_by_identity(app.config['SEED_ADMIN_EMAIL']) is not None:
        return None

    params = {
        'perfil': 'admin',
        'email': app.config['SEED_ADMIN_EMAIL'],
        'senha': app.config['SEED_ADMIN_SENHA']
    }

    return Usuario(**params).save()


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False, help='Create a test db too?')
@click.pass_context
def reset(ctx, with_testdb):
    """
    Init and seed automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed)

    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset)

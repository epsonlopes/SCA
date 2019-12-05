from sca.extensions import mail
from sca.blueprints.contato.tasks import deliver_contact_email


class TestTasks(object):
    def test_deliver_support_email(self):
        """ Deliver a contact email. """
        form = {
          'email': 'email@dominio.com',
          'message': 'Mensagem de teste de TASK do SCA validando a funcionalidade de envio de email no formulario de contato'
        }

        with mail.record_messages() as outbox:
            deliver_contact_email(form.get('email'), form.get('message'))

            assert len(outbox) == 1
            assert form.get('email') in outbox[0].body
from flask import url_for
from lib.tests import assert_status_with_message


class TestContato(object):
    def test_contato_page(self, client):
        """ Contact page should respond with a success 200. """
        response = client.get(url_for('contato.index'))
        assert response.status_code == 200


    def test_contato_form(self, client):
        """ Contact form should redirect with a message. """
        form = {
          'email': 'email@dominio.com',
          'message': 'Mensagem de teste do FORM do SCA validando a funcionalidade de envio de email no formulario de contato.'
        }

        response = client.post(url_for('contato.index'), data=form, follow_redirects=True)
        assert_status_with_message(200, response, 'Obrigado')
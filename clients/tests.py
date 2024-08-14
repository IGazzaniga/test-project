from django.test import TestCase
from unittest.mock import patch
from clients.service import ClientsService
from clients.models import Client
from django.db.utils import IntegrityError
from django.db import transaction

EXAMPLE_EMAIL = 'someexample@miemail.com'

class ClientsModelsTests(TestCase):
    def test_client_str_method_ok(self):
        client = Client.objects.create(email=EXAMPLE_EMAIL)
        self.assertEqual(str(client), EXAMPLE_EMAIL)


@patch('clients.service.logger')
class ClientsServiceTests(TestCase):
    def test_create_user_method_ok(self, mock_logger):
        ClientsService().create_client(email=EXAMPLE_EMAIL)
        mock_logger.info.assert_called_with('Client someexample@miemail.com created successfully')
        self.assertEqual(Client.objects.count(), 1)

    def test_create_user_method_fails(self, mock_logger):
        ClientsService().create_client(email=EXAMPLE_EMAIL)
        self.assertEqual(Client.objects.count(), 1)
        with (self.assertRaises(IntegrityError), transaction.atomic()):
            ClientsService().create_client(email=EXAMPLE_EMAIL)
            mock_logger.error.assert_called_with('Client with email someexample@miemail.com already exists')
        self.assertEqual(Client.objects.count(), 1)

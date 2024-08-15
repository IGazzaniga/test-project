import uuid
from django.test import TestCase
from unittest.mock import patch
from notifications.models import Notification, NotificationType
from notifications.service import NotificationsService, IncorrectNotificationTypeError
from clients.models import Client
from clients.service import ClientDoesNotExistError
from rates.service import RateLimitError

EXAMPLE_NAME = 'TEST'
EXAMPLE_EMAIL = 'someexample@miemail.com'

class NotificationModelsTests(TestCase):
    def setUp(self):
        self.notif_type = NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)

    def test_notification_type_str_method_ok(self):
        self.assertEqual(str(self.notif_type), EXAMPLE_NAME)
    
    def test_notification_str_method_ok(self):
        client = Client.objects.create(email=EXAMPLE_EMAIL)
        notif = Notification.objects.create(notification_type=self.notif_type, client=client, message='Hello')
        self.assertEqual(str(notif), f'{notif.datetime} {EXAMPLE_NAME} - {EXAMPLE_EMAIL}')

@patch('notifications.service.logger')
class NotificationsServiceTests(TestCase):
    @patch('rates.service.RateLimitsService.check_if_rate_is_ok', return_value=True)
    def test_send_notification_successfully_rate_ok(self, mock_rate, mock_logger):
        notif_type = NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)
        client = Client.objects.create(email=EXAMPLE_EMAIL)
        NotificationsService().send_notification(notif_type=EXAMPLE_NAME, client_uuid=client.uuid, message='Hello world')
        mock_logger.info.assert_called_with(f'Notification of type {EXAMPLE_NAME} sent to client {client.uuid} successfully')
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.client, client)
        self.assertEqual(notification.notification_type, notif_type)
        self.assertEqual(notification.message, 'Hello world')

    @patch('rates.service.RateLimitsService.check_if_rate_is_ok', side_effect=RateLimitError)
    def test_send_notification_error_rate_not_enough(self, mock_rate, mock_logger):
        client = Client.objects.create(email=EXAMPLE_EMAIL)
        NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)
        with self.assertRaises(RateLimitError):
            NotificationsService().send_notification(notif_type=EXAMPLE_NAME, client_uuid=client.uuid, message='Hello world')
            mock_logger.warning.assert_called_with(f'Notification of type {EXAMPLE_NAME} cannot be sent to client {client.uuid} due to rate limits')        
            self.assertEqual(Notification.objects.count(), 0)

    def test_send_notification_error_client_does_not_exist(self, mock_logger):
        random_uuid = uuid.uuid4()
        NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)
        with self.assertRaises(ClientDoesNotExistError):
            NotificationsService().send_notification(notif_type=EXAMPLE_NAME, client_uuid=random_uuid, message='Hello world')
            mock_logger.warning.assert_called_with(f'Client with uuid {random_uuid} does not exist')        
            self.assertEqual(Notification.objects.count(), 0)

    def test_send_notification_error_notification_type_does_not_exist(self, mock_logger):
        client = Client.objects.create(email=EXAMPLE_EMAIL)
        with self.assertRaises(IncorrectNotificationTypeError):
            NotificationsService().send_notification(notif_type='RANDOM', client_uuid=client.uuid, message='Hello world')
            mock_logger.error.assert_called_with(f'Notification type RANDOM does not exist')        
            self.assertEqual(Notification.objects.count(), 0)
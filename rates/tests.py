from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from unittest.mock import patch
from notifications.models import NotificationType
from rates.service import RateLimitsService, RateLimitError
from clients.models import Client

EXAMPLE_NAME = 'TEST'

@patch('rates.service.logger')
class RateLimitsServiceTests(TestCase):
    def test_create_notification_type_with_rate_ok(self, mock_logger):
        RateLimitsService().create_notification_type_with_rate(name='Something', max_times=1, minutes=1)
        mock_logger.info.assert_called_with('Notification type Something successfully created')
        self.assertEqual(NotificationType.objects.count(), 1)

    def test_create_notification_type_method_fails_existing_type_with_same_name(self, mock_logger):
        RateLimitsService().create_notification_type_with_rate(name=EXAMPLE_NAME, max_times=1, minutes=1)
        self.assertEqual(NotificationType.objects.count(),1)
        with (self.assertRaises(IntegrityError), transaction.atomic()):
            RateLimitsService().create_notification_type_with_rate(name=EXAMPLE_NAME, max_times=1, minutes=1)
            mock_logger.error.assert_called_with('Notification type TEST already exists or some value is incorrect. Please check')        
        self.assertEqual(NotificationType.objects.count(),1)

    def test_create_notification_type_method_fails_invalid_values(self, mock_logger):
        with (self.assertRaises(IntegrityError), transaction.atomic()):
            RateLimitsService().create_notification_type_with_rate(name=EXAMPLE_NAME, max_times=-1, minutes=1)
            mock_logger.error.assert_called_with(f'Notification type {EXAMPLE_NAME} already exists or some value is incorrect. Please check')        
        self.assertEqual(NotificationType.objects.count(),0)

        with (self.assertRaises(IntegrityError), transaction.atomic()):
            RateLimitsService().create_notification_type_with_rate(name=EXAMPLE_NAME, max_times=1, minutes=-1)
            mock_logger.error.assert_called_with(f'Notification type {EXAMPLE_NAME} already exists or some value is incorrect. Please check')        
        self.assertEqual(NotificationType.objects.count(),0)

    def test_edit_notification_type_rate_ok(self, mock_logger):
        NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)
        self.assertEqual(NotificationType.objects.count(), 1)
        RateLimitsService().edit_notification_type_rate(name=EXAMPLE_NAME, max_times=2, minutes=7)
        self.assertEqual(NotificationType.objects.count(), 1)
        notif_type = NotificationType.objects.first()
        self.assertEqual(notif_type.max_times_allowed, 2)
        self.assertEqual(notif_type.minutes, 7)
        mock_logger.info.assert_called_with(f'Notification type {EXAMPLE_NAME} successfully updated')

    def test_edit_notification_type_rate_method_fails_invalid_values(self, mock_logger):
        notif_type = NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=1, minutes=100)
        with (self.assertRaises(IntegrityError), transaction.atomic()):
            RateLimitsService().edit_notification_type_rate(name=EXAMPLE_NAME, max_times=-1, minutes=1)
            mock_logger.error.assert_called_with(f'Notification type {EXAMPLE_NAME} update failed because some value is incorrect. Please check')        
        self.assertEqual(notif_type.max_times_allowed, 1)
        self.assertEqual(notif_type.minutes, 100)


        with (self.assertRaises(IntegrityError), transaction.atomic()):
            RateLimitsService().create_notification_type_with_rate(name=EXAMPLE_NAME, max_times=1, minutes=-1)
            mock_logger.error.assert_called_with(f'Notification type {EXAMPLE_NAME} already exists or some value is incorrect. Please check')        
        self.assertEqual(notif_type.max_times_allowed, 1)
        self.assertEqual(notif_type.minutes, 100)

    def test_check_if_rate_is_ok_ok(self, mock_logger):
        notif_type_obj = NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=2, minutes=60)
        client = Client.objects.create(email='someexample@miemail.com')
        
        self.assertTrue(RateLimitsService().check_if_rate_is_ok(notif_type_obj, client.uuid))

    def test_check_if_rate_is_ok_raises_error(self, mock_logger):
        notif_type_obj = NotificationType.objects.create(name=EXAMPLE_NAME, max_times_allowed=0, minutes=60)
        client = Client.objects.create(email='someexample@miemail.com')
        
        with self.assertRaises(RateLimitError):
            RateLimitsService().check_if_rate_is_ok(notif_type_obj, client.uuid)
import logging
import uuid
from datetime import datetime, timedelta
from notifications.models import Notification, NotificationType
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

class RateLimitsService:
    def create_notification_type_with_rate(self, name: str, max_times: int, minutes: int):
        """
        Create a NotificationType with a given name, max times allowed and minutes.
        If a NotificationType with the same name exists, raise an IntegrityError
        If the max_times parameter is not a positive integer, raise an IntegrityError
        If the minutes parameter is not a positive integer, raise an IntegrityError
        """
        try:
            NotificationType.objects.create(
                name=name,
                max_times_allowed=max_times,
                minutes=minutes
            )
        except IntegrityError:
             logger.error(f'Notification type {name} already exists or some value is incorrect. Please check')
             raise
        
        logger.info(f'Notification type {name} successfully created')
        return

    def edit_notification_type_rate(self, name: str, max_times: int, minutes: int):
        """
        Edit a NotificationType with a given name. 
        The max times allowed and minutes can be edited.
        If the max_times parameter is not a positive integer, raise an IntegrityError
        If the minutes parameter is not a positive integer, raise an IntegrityError
        """
        try:
            NotificationType.objects.filter(name=name).update(max_times_allowed=max_times, minutes=minutes)
        except IntegrityError:
            logger.error(f'Notification type {name} update failed because some value is incorrect. Please check')
            raise
        else:
            logger.info(f'Notification type {name} successfully updated')

        return

    def check_if_rate_is_ok(
            self,
            notif_type: object,
            client_uuid: uuid.UUID,
        ):
        """
        Check if a certain notification type can be sent to a user, based on rate limits.
        For this, the Notifications of a certain type between now and the specified minutes must be counted.
        If the amount is lower, the notification can be sent.
        Otherwise, raise a custom RateLimitError exception.
        """
        date_to = datetime.now()
        date_from = date_to - timedelta(minutes=notif_type.minutes)
        max_times = notif_type.max_times_allowed

        if Notification.objects.filter(
            client__uuid=client_uuid,
            notification_type=notif_type,
            datetime__gte=date_from,
            datetime__lt=date_to
        ).count() >= max_times:
            raise RateLimitError
        
        return True

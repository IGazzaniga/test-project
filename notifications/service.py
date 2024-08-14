import logging
import uuid
from notifications.models import Notification, NotificationType
from datetime import datetime, timedelta
from django.db.utils import IntegrityError
from rates.service import RateLimitsService
from clients.service import ClientsService, ClientDoesNotExistError

logger = logging.getLogger(__name__)

class IncorrectNotificationTypeError(Exception):
    pass

class NotificationService:
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

    def send_notification(self, notif_type: str, client_uuid: uuid.UUID, message: str):
        """
        Sends a Notification of a specific type to a Client.
        First, it checks if the type exists. If not, raise a custom IncorrectNotificationTypeError exception.
        Then, check if the Client with the provided uuid exists. If not, raise a custom ClientDoesNotExistError exception.
        
        
        Then, pass the date range to the RateLimitsService to check if the notification type
        can be sent to the provided Client.

        If everything is ok, create a Notification of the specific type to the provided Client with
        the provided message and set the datetime as the current datetime.
        """
        try:
            notif_type_obj = NotificationType.objects.get(name=notif_type)
        except NotificationType.DoesNotExist:
            logger.error(f'Notification type {notif_type} does not exist')
            raise IncorrectNotificationTypeError

        try:
            client = ClientsService().get_client_by_uuid(uuid=client_uuid)
        except ClientDoesNotExistError:
            raise
        

        date_to = datetime.now()
        date_from = date_to - timedelta(minutes=notif_type_obj.minutes)
        max_times = notif_type_obj.max_times_allowed

        if not RateLimitsService().check_if_rate_is_ok(notif_type, client_uuid, date_from, date_to, max_times):
            logger.warning(f'Notification of type {notif_type} cannot be sent to client {client_uuid} due to rate limits')
            return
        
        Notification.objects.create(
            client=client,
            notification_type=notif_type_obj,
            message=message,
            datetime=datetime.now()
        )
        logger.info(f'Notification of type {notif_type} sent to client {client_uuid} successfully')
        return
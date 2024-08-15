import logging
import uuid
from notifications.models import Notification, NotificationType
from datetime import datetime
from rates.service import RateLimitsService, RateLimitError
from clients.service import ClientsService, ClientDoesNotExistError

logger = logging.getLogger(__name__)

class IncorrectNotificationTypeError(Exception):
    pass

class NotificationsService:
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
            client = ClientsService().get_client_by_uuid(uuid=client_uuid)
        except ClientDoesNotExistError:
            raise
        
        try:
            notif_type_obj = NotificationType.objects.get(name=notif_type)
        except NotificationType.DoesNotExist:
            logger.error(f'Notification type {notif_type} does not exist')
            raise IncorrectNotificationTypeError

        try:
            RateLimitsService().check_if_rate_is_ok(notif_type_obj, client_uuid)
        except RateLimitError:
            logger.warning(f'Notification of type {notif_type} cannot be sent to client {client_uuid} due to rate limits')
            raise
        
        Notification.objects.create(
            client=client,
            notification_type=notif_type_obj,
            message=message,
            datetime=datetime.now()
        )
        logger.info(f'Notification of type {notif_type} sent to client {client_uuid} successfully')
        return
import logging
from notifications.models import Notification, NotificationType
from datetime import datetime, timedelta
from django.db.utils import IntegrityError
from rates.service import RateLimitsService
from clients.service import ClientsService, ClientDoesNotExistError

logger = logging.getLogger(__name__)

class IncorrectNotificationTypeError(Exception):
    pass

class NotificationService:
    def create_notification_type_with_rate(self, name, max_times, minutes):
        try:
            NotificationType.objects.create(
                name=name,
                max_times_allowed=max_times,
                minutes=minutes
            )
        except IntegrityError:
             logger.error(f"Notification type {name} already exists or some value is incorrect. Please check")
             raise
        
        logger.info(f"Notification type {name} successfully created")
        return

    def edit_notification_type_rate(self, name, max_times, minutes):
        try:
            NotificationType.objects.filter(name=name).update(max_times_allowed=max_times, minutes=minutes)
        except IntegrityError:
            logger.error(f"Notification type {name} update failed because some value is incorrect. Please check")
            raise
        else:
            logger.info(f"Notification type {name} successfully updated")

        return

    def send_notification(self, notif_type, client_uuid, message):
        try:
            notif_type_obj = NotificationType.objects.get(name=notif_type)
        except NotificationType.DoesNotExist:
            logger.error(f'Notification type {notif_type} does not exist')
            raise IncorrectNotificationTypeError

        date_to = datetime.now()
        date_from = date_to - timedelta(minutes=notif_type_obj.minutes)
        max_times = notif_type_obj.max_times_allowed


        try:
            client = ClientsService().get_client_by_uuid(uuid=client_uuid)
        except ClientDoesNotExistError:
            raise
            
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
import uuid
from datetime import datetime
from notifications.models import Notification

class RateLimitsService:
    def check_if_rate_is_ok(
            self,
            notif_type: str,
            client_uuid: uuid.UUID,
            date_from: datetime,
            date_to: datetime,
            max_times: int
        ):
        """
        Check if a certain notification type can be sent to a user, based on rate limits.
        For this, the Notifications of a certain type between now and the specified minutes must be counted.
        If the amount is lower, the notification can be sent. Otherwise, deny it.
        """
        return Notification.objects.filter(
            client__uuid=client_uuid,
            notification_type__name=notif_type,
            datetime__gte=date_from,
            datetime__lt=date_to
        ).count() < max_times

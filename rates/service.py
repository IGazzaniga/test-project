from notifications.models import Notification, NotificationType

class RateLimitsService:
    def check_if_rate_is_ok(self, notif_type, client_uuid, date_from, date_to, max_times):
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

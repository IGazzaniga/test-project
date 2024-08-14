from django.db import models
from clients.models import Client
# Create your models here.

class NotificationType(models.Model):
    """
    Model for storing the different Notification types.
    Any time a new type is needed, just create an object with the corresponding name, max times allowed and the 
    measurement unit in minutes
    e.g. A type with a max of 3 times in 1 week (10080 minutes)
    NotificationType.objects.create(
        name='Example',
        max_times_allowed=3,
        minutes=10080 
    )
    """
    name = models.CharField(max_length=254, db_index=True, unique=True)
    max_times_allowed = models.PositiveSmallIntegerField()
    # The amount of minutes to express the desired unit
    # e.g 60 for an hour, 1440 for a day, 10080 for a week
    minutes = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Notification(models.Model):
    """
    Model for storing the notifications sent to a user.
    The datetime combined with the notification_type will be used to check the limit rates.
    """
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.PROTECT, related_name='notifications')
    message = models.TextField()
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.datetime} {self.notification_type} - {self.client}"

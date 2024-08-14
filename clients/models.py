import uuid
from django.db import models

# Create your models here.

class Client(models.Model):
    """
    Model for storing the clients
    """
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.email
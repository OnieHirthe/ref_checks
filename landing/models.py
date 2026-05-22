from django.db import models
import datetime as dt
import uuid
import csv
from django.utils.timezone import now as NOW


class SubscriberManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class Subscriber(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=300)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=NOW)

    objects = SubscriberManager()

    def __str__(self):
        return self.email

from django.db import models
import datetime as dt
import uuid
from pytz import UTC
import csv

def NOW():
    return dt.datetime.now().replace(tzinfo=UTC)


class SubscriberManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def to_csv(self, **kwargs):
        timestamp = str(dt.datetime.now()).replace(' ', '_').replace(':', '_')
        filename = f"/home/annas/kmu_files/subscribers_{timestamp}.csv"
        with open(filename, "w+") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["email", "comment", "created"])
            subs = self.all()
            for sub in subs:
                writer.writerow([sub.email, sub.comment, sub.created])

class Subscriber(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=300)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=NOW)

    objects = SubscriberManager()

    def __str__(self):
        return self.email

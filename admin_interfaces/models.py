from django.db import models
from users.models import Profile, Report, UserAuth
from django.utils.timezone import now as NOW
import uuid

class Comment(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    content = models.TextField(blank=True, null=True)
    
    created = models.DateTimeField(default=NOW)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comments")
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="comments")
    auto = models.BooleanField(default=False)

class BlackListedEntry(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    level = models.CharField(max_length=100, default="gray", choices=(('gray', "Серый список"), ('black', "Черный список")))
    # who is associated in the system
    user = models.OneToOneField(UserAuth, on_delete=models.SET_NULL, blank=True, null=True, related_name="in_bl")
    comment = models.TextField()

    # who created entry
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="bl_entries")
    created = models.DateTimeField(default=NOW)



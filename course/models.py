from authentication.models import User
from django.db import models
import uuid


class Course(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(default="", max_length=120, null=True, blank=True)
    short_description = models.TextField(default="", null=True, blank=True)
    long_description = models.TextField(default="", null=True, blank=True)
    price = models.IntegerField(default=0)
    offer = models.IntegerField(default=0)
    duration = models.CharField(default="", null=True, blank=True)
    thumbnail = models.CharField(max_length=120, default="", null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        default="draft",
    )
    videoURL = models.CharField(default="", max_length=120, blank=True, null=True)
    notesURL = models.CharField(default="", max_length=120, blank=True, null=True)
    presentationURL = models.CharField(
        default="", max_length=120, blank=True, null=True
    )
    codeURL = models.CharField(default="", max_length=120, blank=True, null=True)
    content = models.TextField(default="", null=True, blank=True)
    created_at = models.CharField(max_length=50)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Course, self).save(*args, **kwargs)

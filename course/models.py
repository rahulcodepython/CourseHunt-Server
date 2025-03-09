from django.contrib.postgres.fields import ArrayField
from authentication.models import User
from django.db import models
import uuid


class Course(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(default="", max_length=120, null=True, blank=True)
    short_description = models.TextField(default="", null=True, blank=True)
    long_description = models.TextField(default="", null=True, blank=True)
    price = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    language = ArrayField(
        models.CharField(max_length=10, blank=True),
        size=3,
        default=list,
        null=True,
        blank=True,
    )
    rating = models.FloatField(default=0.0)
    learners = models.IntegerField(default=0)
    tags = ArrayField(
        models.CharField(max_length=50, blank=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )
    offer = models.FloatField(default=0.0)
    duration = models.CharField(default="", null=True, blank=True)
    thumbnail = models.CharField(max_length=1000, default="", null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        default="draft",
    )
    videoURL = models.CharField(default="", max_length=1000, blank=True, null=True)
    notesURL = models.CharField(default="", max_length=1000, blank=True, null=True)
    presentationURL = models.CharField(
        default="", max_length=1000, blank=True, null=True
    )
    codeURL = models.CharField(default="", max_length=1000, blank=True, null=True)
    content = models.TextField(default="", null=True, blank=True)
    includes = ArrayField(
        models.CharField(max_length=1000, blank=True, null=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )
    requirements = ArrayField(
        models.CharField(max_length=1000, blank=True, null=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Course, self).save(*args, **kwargs)

from authentication.models import User
from django.db import models
import uuid

# Create your models here.


class Feedback(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField(default="", null=True, blank=True)
    rating = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        if self.rating < 0:
            self.rating = 0
        elif self.rating > 5:
            self.rating = 5

        super(Feedback, self).save(*args, **kwargs)

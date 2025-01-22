from authentication.models import User
from django.db import models
import uuid


class Blog(models.Model):
    id = models.CharField(
        max_length=100, primary_key=True, unique=True, editable=False, db_index=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.CharField(max_length=1000)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    likes = models.IntegerField(default=0)
    like = models.ManyToManyField(User, related_name="liked_blogs", blank=True)
    read = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Blog, self).save(*args, **kwargs)


class Comment(models.Model):
    id = models.CharField(
        max_length=100, primary_key=True, unique=True, editable=False, db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super(Comment, self).save(*args, **kwargs)

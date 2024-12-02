from authentication.models import User
from django.db import models
import uuid


class Course(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(default="", max_length=120, null=True, blank=True)
    short_description = models.TextField(default="", null=True, blank=True)
    long_description = models.TextField(default="", null=True, blank=True)
    price = models.IntegerField(default=0)
    offer = models.FloatField(default=0.0)
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


class Purchase(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

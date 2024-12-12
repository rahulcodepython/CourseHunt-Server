from django.db import models
from course.models import Course
from authentication.models import User
import uuid


class Purchase(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Purchase, self).save(*args, **kwargs)


class CuponeCode(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    code = models.CharField(max_length=10, unique=True)
    discount = models.IntegerField()
    expiry = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(null=True, blank=True)
    used = models.IntegerField(default=0)
    is_unlimited = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(CuponeCode, self).save(*args, **kwargs)

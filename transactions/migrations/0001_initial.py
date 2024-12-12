# Generated by Django 5.1.2 on 2024-12-12 13:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0017_delete_cuponecode_delete_purchase'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CuponeCode',
            fields=[
                ('id', models.CharField(editable=False, max_length=120, primary_key=True, serialize=False, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('discount', models.IntegerField()),
                ('expiry', models.DateField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('used', models.IntegerField(default=0)),
                ('is_unlimited', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.CharField(editable=False, max_length=120, primary_key=True, serialize=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=100, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

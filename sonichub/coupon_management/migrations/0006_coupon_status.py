# Generated by Django 5.0 on 2024-02-07 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon_management', '0005_remove_coupon_is_active_users_coupon_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
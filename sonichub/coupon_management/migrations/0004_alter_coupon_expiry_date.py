# Generated by Django 5.0.1 on 2024-01-25 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon_management', '0003_alter_coupon_expiry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiry_date',
            field=models.DateField(),
        ),
    ]
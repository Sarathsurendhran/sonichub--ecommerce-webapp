# Generated by Django 5.0 on 2024-01-21 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category_management', '0004_category_date_category_discount_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='date',
            new_name='expirydate',
        ),
    ]

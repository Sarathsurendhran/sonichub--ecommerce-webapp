# Generated by Django 5.0 on 2024-01-03 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_panel', '0002_address_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(default='sarath', max_length=50),
        ),
    ]

# Generated by Django 5.0 on 2023-12-20 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_authentication', '0003_alter_userprofile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, unique=True),
        ),
    ]

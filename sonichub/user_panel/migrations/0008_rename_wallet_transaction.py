# Generated by Django 5.0 on 2024-01-15 08:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_panel', '0007_alter_wallet_amount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Wallet',
            new_name='Transaction',
        ),
    ]

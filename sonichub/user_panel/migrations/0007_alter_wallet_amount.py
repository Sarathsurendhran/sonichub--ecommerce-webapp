# Generated by Django 5.0 on 2024-01-15 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_panel', '0006_wallet_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]

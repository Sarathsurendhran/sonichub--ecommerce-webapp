# Generated by Django 5.0 on 2024-01-21 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category_management', '0005_rename_date_category_expirydate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='expirydate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='minimum_amount',
            field=models.CharField(max_length=40, null=True),
        ),
    ]

# Generated by Django 5.1.1 on 2025-01-09 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Flightapp', '0015_bookedflights_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='useradditionalinfo',
            name='is_default_password',
            field=models.BooleanField(default=True),
        ),
    ]

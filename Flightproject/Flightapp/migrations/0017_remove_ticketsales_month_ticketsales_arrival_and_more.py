# Generated by Django 5.1.1 on 2025-01-09 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Flightapp', '0016_useradditionalinfo_is_default_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketsales',
            name='month',
        ),
        migrations.AddField(
            model_name='ticketsales',
            name='arrival',
            field=models.DateField(blank=True, null=True, verbose_name='Arrival Date'),
        ),
        migrations.AddField(
            model_name='ticketsales',
            name='flight_num',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Flight Number'),
        ),
        migrations.AddField(
            model_name='ticketsales',
            name='return_date',
            field=models.DateField(blank=True, max_length=50, null=True, verbose_name='Return Date'),
        ),
    ]

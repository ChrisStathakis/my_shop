# Generated by Django 2.0 on 2018-08-21 12:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentorders',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 21, 12, 17, 42, 956739, tzinfo=utc)),
        ),
    ]
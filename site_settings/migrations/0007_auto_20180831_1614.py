# Generated by Django 2.0 on 2018-08-31 13:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0006_auto_20180831_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentorders',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 31, 13, 14, 2, 756846, tzinfo=utc)),
        ),
    ]

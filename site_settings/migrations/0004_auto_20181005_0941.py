# Generated by Django 2.0.5 on 2018-10-05 06:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0003_auto_20181005_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentorders',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 5, 6, 41, 1, 929, tzinfo=utc)),
        ),
    ]

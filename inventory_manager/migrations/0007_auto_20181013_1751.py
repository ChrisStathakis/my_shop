# Generated by Django 2.0.5 on 2018-10-13 14:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0006_auto_20181005_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 13, 14, 51, 2, 130622, tzinfo=utc)),
        ),
    ]

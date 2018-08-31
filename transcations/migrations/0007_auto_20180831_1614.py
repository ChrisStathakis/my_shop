# Generated by Django 2.0 on 2018-08-31 13:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('transcations', '0006_auto_20180831_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 31, 13, 14, 2, 756846, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='genericexpense',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 31, 13, 14, 2, 756846, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 31, 13, 14, 2, 756846, tzinfo=utc)),
        ),
    ]
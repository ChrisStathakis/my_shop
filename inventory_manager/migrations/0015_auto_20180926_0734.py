# Generated by Django 2.0.5 on 2018-09-26 04:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0014_auto_20180926_0733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='size',
        ),
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 9, 26, 4, 33, 59, 792565, tzinfo=utc)),
        ),
    ]
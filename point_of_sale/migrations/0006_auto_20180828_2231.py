# Generated by Django 2.0.5 on 2018-08-28 19:31

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0005_auto_20180824_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailorder',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 8, 28, 19, 31, 42, 163296, tzinfo=utc)),
        ),
    ]
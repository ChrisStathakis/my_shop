# Generated by Django 2.0 on 2018-09-17 16:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0010_auto_20180917_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailorder',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 9, 17, 16, 6, 5, 394931, tzinfo=utc)),
        ),
    ]
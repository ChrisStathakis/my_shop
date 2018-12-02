# Generated by Django 2.0 on 2018-10-16 14:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('transcations', '0007_auto_20181015_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 16, 14, 11, 43, 179396, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='genericexpense',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 16, 14, 11, 43, 179396, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 16, 14, 11, 43, 179396, tzinfo=utc)),
        ),
    ]
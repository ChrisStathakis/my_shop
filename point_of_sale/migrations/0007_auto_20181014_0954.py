# Generated by Django 2.0.5 on 2018-10-14 06:54

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20181014_0954'),
        ('point_of_sale', '0006_auto_20181013_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retailorder',
            name='address',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='cellphone',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='city',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='costumer_submit',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='email',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='state',
        ),
        migrations.RemoveField(
            model_name='retailorder',
            name='zip_code',
        ),
        migrations.AddField(
            model_name='retailorder',
            name='address_profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Address'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2018, 10, 14, 6, 54, 40, 124671, tzinfo=utc)),
        ),
    ]
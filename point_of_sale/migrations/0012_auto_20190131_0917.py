# Generated by Django 2.0.5 on 2019-01-31 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0011_auto_20190130_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailorderitem',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
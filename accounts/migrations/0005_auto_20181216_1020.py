# Generated by Django 2.0.5 on 2018-12-16 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20181216_1020'),
        ('point_of_sale', '0008_auto_20181216_1020'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
        migrations.DeleteModel(
            name='BillingProfile',
        ),
    ]
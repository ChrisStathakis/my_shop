# Generated by Django 2.0.5 on 2019-01-31 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0006_auto_20190130_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentorders',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='paymentorders',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='paymentorders',
            name='user_account',
        ),
        migrations.DeleteModel(
            name='PaymentOrders',
        ),
    ]

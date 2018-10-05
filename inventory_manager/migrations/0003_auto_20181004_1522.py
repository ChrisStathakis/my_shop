# Generated by Django 2.0 on 2018-10-04 12:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('site_settings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory_manager', '0002_auto_20181004_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.PaymentMethod'),
        ),
        migrations.AddField(
            model_name='order',
            name='user_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor_orders', to='inventory_manager.Vendor', verbose_name='Vendor'),
        ),
        migrations.AlterUniqueTogether(
            name='orderitemsize',
            unique_together={('order_item_related', 'size_related')},
        ),
    ]
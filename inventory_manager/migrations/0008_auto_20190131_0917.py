# Generated by Django 2.0.5 on 2019-01-31 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0007_auto_20190130_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_product', to='products.Product', verbose_name='Προϊόν'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

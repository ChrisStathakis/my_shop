# Generated by Django 2.0.5 on 2018-12-02 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('carts', '0003_auto_20181202_1511'),
        ('site_settings', '0001_initial'),
        ('products', '0001_initial'),
        ('point_of_sale', '0002_auto_20181202_1511'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='retailorder',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='site_settings.PaymentMethod'),
        ),
        migrations.AddField(
            model_name='retailorder',
            name='seller_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='retailorder',
            name='shipping',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.Shipping'),
        ),
        migrations.AddField(
            model_name='retailorder',
            name='user_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='giftretailitem',
            name='cart_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.Cart'),
        ),
        migrations.AddField(
            model_name='giftretailitem',
            name='order_related',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifts', to='point_of_sale.RetailOrder'),
        ),
        migrations.AddField(
            model_name='giftretailitem',
            name='product_related',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
    ]
# Generated by Django 2.0 on 2018-06-24 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import inventory_manager.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0005_auto_20180608_1813'),
        ('site_settings', '0004_store'),
        ('inventory_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_expired', models.DateTimeField(auto_created=True)),
                ('title', models.CharField(max_length=150)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('taxes', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('is_paid', models.BooleanField(default=False)),
                ('printed', models.BooleanField(default=False)),
                ('total_price_no_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία προ έκπτωσης')),
                ('total_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία έκπτωσης')),
                ('total_price_after_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία μετά την έκπτωση')),
                ('total_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Φ.Π.Α')),
                ('final_price', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Τελική Αξία')),
                ('taxes_modifier', models.CharField(choices=[('1', '13'), ('2', '23'), ('3', '24'), ('4', '0')], default='3', max_length=1)),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.PaymentMethod')),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Vendor', verbose_name='Προμηθευτής')),
            ],
            options={
                'verbose_name_plural': '1. Τιμολόγια',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(choices=[('1', 'Τεμάχια'), ('2', 'Κιλά'), ('3', 'Κιβώτια')], default='1', max_length=1)),
                ('discount', models.IntegerField(default=0, verbose_name='Εκπτωση %')),
                ('taxes', models.CharField(choices=[('1', '13'), ('2', '23'), ('3', '24'), ('4', '0')], default='3', max_length=1)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Ποσότητα')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, verbose_name='Τιμή Μονάδας')),
                ('total_clean_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Συνολική Αξία χωρίς Φόρους')),
                ('total_value_with_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Συνολική Αξία με φόρους')),
                ('day_added', models.DateField(blank=True, null=True)),
                ('final_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Προϊόν')),
                ('size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.SizeAttribute', verbose_name='Size')),
            ],
            options={
                'verbose_name': 'Συστατικά Τιμολογίου   ',
                'ordering': ['product'],
            },
        ),
        migrations.CreateModel(
            name='PreOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('a', 'Active'), ('b', 'Used')], default='a', max_length=1)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseOrderImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to=inventory_manager.models.upload_image, validators=[inventory_manager.models.validate_file])),
                ('is_first', models.BooleanField(default=True)),
                ('order_related', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order')),
            ],
        ),
    ]
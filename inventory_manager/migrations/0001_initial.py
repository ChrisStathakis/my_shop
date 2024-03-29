# Generated by Django 2.0.5 on 2019-02-07 06:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import inventory_manager.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=70, unique=True, verbose_name='Τίτλος Κατηγορίας')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Περιγραφή')),
            ],
            options={
                'verbose_name': '3. Κατηγορίες Αποθήκης',
                'verbose_name_plural': '3. Κατηγορίες Αποθήκης',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')),
                ('title', models.CharField(max_length=150)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('date_expired', models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία')),
                ('taxes', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Φόροι')),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Πληρωτέο Ποσό')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Τελική Αξίσ')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Επιπλέον Έκπτωση')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Πληρωμένο?')),
                ('printed', models.BooleanField(default=False)),
                ('total_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Συνολική Έκπτωση')),
                ('total_price_after_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Καθαρή Έκπτωση')),
                ('taxes_modifier', models.CharField(choices=[('1', 13), ('2', 23), ('3', 24), ('4', 0)], default='3', max_length=1)),
                ('total_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Συνολικοί Φόροι')),
                ('order_type', models.CharField(choices=[('1', 'Τιμολόγιο - Δελτίο Αποστολής'), ('2', 'Τιμολόγιο'), ('3', 'Δελτίο Απόστολης'), ('4', 'Εισαγωγή Αποθήκης'), ('5', 'Εξαγωγή Αποθήκης')], default=1, max_length=1)),
            ],
            options={
                'verbose_name_plural': '1. Warehouse Invoice',
                'ordering': ['-date_expired'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True, verbose_name='Ημερομηνία Τελευταίας Επεξεργασίας')),
                ('qty', models.PositiveIntegerField(default=1, verbose_name='Ποσότητα')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Άρχικη Αξία')),
                ('discount_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Ποσοστό Έκτωσης')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία')),
                ('unit', models.CharField(choices=[('1', 'Τεμάχια'), ('2', 'Κιλά'), ('3', 'Κιβώτια')], default='1', max_length=1, verbose_name='Μονάδα Μέτρησης')),
                ('taxes', models.CharField(choices=[('1', 13), ('2', 23), ('3', 24), ('4', 0)], default='3', max_length=1, verbose_name='ΦΠΑ')),
                ('total_clean_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Συνολική Αξία χωρίς Φόρους')),
                ('total_value_with_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Συνολική Αξία με φόρους')),
            ],
            options={
                'verbose_name': 'Συστατικά Τιμολογίου',
                'ordering': ['product'],
            },
        ),
        migrations.CreateModel(
            name='OrderItemSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('discount', models.IntegerField(default=0)),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
            ],
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
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('year', models.DateField()),
                ('printscreen', models.BooleanField(default=False)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
            ],
            options={
                'ordering': ['year'],
            },
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('price_buy', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('order_related', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory_manager.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='TaxesCity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'verbose_name': 'ΔΟΥ   ',
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=70, unique=True, verbose_name="'Ονομα")),
                ('afm', models.CharField(blank=True, max_length=9, null=True, verbose_name='ΑΦΜ')),
                ('phone', models.CharField(blank=True, max_length=10, null=True, verbose_name='Τηλέφωνο')),
                ('phone1', models.CharField(blank=True, max_length=10, null=True, verbose_name='Τηλέφωνο')),
                ('fax', models.CharField(blank=True, max_length=10, null=True, verbose_name='Fax')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('site', models.CharField(blank=True, max_length=40, null=True, verbose_name='Site')),
                ('address', models.CharField(blank=True, max_length=40, null=True, verbose_name='Διεύθυνση')),
                ('city', models.CharField(blank=True, max_length=40, null=True, verbose_name='Πόλη')),
                ('zip_code', models.CharField(blank=True, max_length=40, null=True, verbose_name='TK')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Περιγραφή')),
                ('date_added', models.DateField(default=django.utils.timezone.now)),
                ('taxes_modifier', models.CharField(choices=[('1', 13), ('2', 23), ('3', 24), ('4', 0)], default='3', max_length=1)),
                ('remaining_deposit', models.DecimalField(decimal_places=2, default=0, max_digits=100, verbose_name='Υπόλοιπο προκαταβολών')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=100, verbose_name='Υπόλοιπο')),
                ('doy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.TaxesCity', verbose_name='Εφορία')),
            ],
            options={
                'verbose_name_plural': '9. Προμηθευτές',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='WarehouseOrderImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to=inventory_manager.models.upload_image, validators=[inventory_manager.models.validate_file])),
                ('is_first', models.BooleanField(default=True)),
                ('order_related', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='inventory_manager.Order')),
            ],
        ),
    ]

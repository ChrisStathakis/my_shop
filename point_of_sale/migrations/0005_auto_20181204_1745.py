# Generated by Django 2.0 on 2018-12-04 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0004_auto_20181202_1845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='retailorder',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Πώληση', 'verbose_name_plural': '1. Παραστατικά Πωλήσεων'},
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Επιπλέον Έκπτωση'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Πληρωμένο?'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='site_settings.PaymentMethod', verbose_name='Τρόπος Πληρωμής'),
        ),
        migrations.AlterField(
            model_name='retailorderitem',
            name='discount_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Ποσοστό Έκτωσης'),
        ),
        migrations.AlterField(
            model_name='retailorderitem',
            name='edited',
            field=models.DateTimeField(auto_now=True, verbose_name='Ημερομηνία Τελευταίας Επεξεργασίας'),
        ),
        migrations.AlterField(
            model_name='retailorderitem',
            name='final_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία'),
        ),
        migrations.AlterField(
            model_name='retailorderitem',
            name='qty',
            field=models.PositiveIntegerField(default=1, verbose_name='Ποσότητα'),
        ),
        migrations.AlterField(
            model_name='retailorderitem',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Άρχικη Αξία'),
        ),
    ]

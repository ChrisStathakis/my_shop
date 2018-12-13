# Generated by Django 2.0 on 2018-12-12 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0005_auto_20181204_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailorder',
            name='date_expired',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='final_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Τελική Αξίσ'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='paid_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Πληρωτέο Ποσό'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='taxes',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Φόροι'),
        ),
        migrations.AlterField(
            model_name='retailorder',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία'),
        ),
    ]
# Generated by Django 2.0 on 2018-08-20 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20180811_2025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brands',
            options={'ordering': ['title'], 'verbose_name_plural': '4. Brands'},
        ),
    ]

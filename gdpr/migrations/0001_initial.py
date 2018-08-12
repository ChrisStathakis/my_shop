# Generated by Django 2.0.5 on 2018-08-11 17:25

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CookiesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('active', models.BooleanField(default=True)),
                ('text', tinymce.models.HTMLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('active', models.BooleanField(default=True)),
                ('text', tinymce.models.HTMLField(blank=True)),
            ],
        ),
    ]

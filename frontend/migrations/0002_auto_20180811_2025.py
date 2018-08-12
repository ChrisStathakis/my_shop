# Generated by Django 2.0.5 on 2018-08-11 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('frontend', '0001_initial'),
        ('site_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.Country'),
        ),
        migrations.AddField(
            model_name='categorysite',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='frontend.CategorySite'),
        ),
        migrations.AlterUniqueTogether(
            name='categorysite',
            unique_together={('slug', 'parent')},
        ),
    ]
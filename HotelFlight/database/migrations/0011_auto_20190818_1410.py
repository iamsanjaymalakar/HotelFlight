# Generated by Django 2.2.3 on 2019-08-18 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0010_auto_20190818_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='Latitude',
            field=models.DecimalField(decimal_places=5, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='Longitude',
            field=models.DecimalField(decimal_places=5, max_digits=10, null=True),
        ),
    ]

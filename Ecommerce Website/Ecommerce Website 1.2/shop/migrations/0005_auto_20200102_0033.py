# Generated by Django 3.0.1 on 2020-01-02 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20191228_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='desc',
            field=models.TextField(max_length=2500),
        ),
        migrations.AlterField(
            model_name='products',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
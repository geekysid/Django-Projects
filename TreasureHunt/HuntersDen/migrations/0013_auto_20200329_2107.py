# Generated by Django 3.0.1 on 2020-03-29 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HuntersDen', '0012_auto_20200329_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riddlelevel',
            name='negetive_score_percent',
            field=models.FloatField(default=0.1),
        ),
        migrations.AlterField(
            model_name='riddlelevel',
            name='positive_score_percent',
            field=models.FloatField(default=1.0),
        ),
    ]

# Generated by Django 3.0.1 on 2020-03-29 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HuntersDen', '0003_auto_20200329_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='den',
            name='invitation_code',
            field=models.CharField(blank=True, editable=False, max_length=10),
        ),
    ]

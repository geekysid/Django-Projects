# Generated by Django 3.0.1 on 2020-03-30 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0007_passwordrecovery'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='uin_code',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]

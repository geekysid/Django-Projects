# Generated by Django 3.0.1 on 2020-03-28 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile',
            name='avatar',
            field=models.ImageField(default='dummy1.jpg', upload_to='image/profile_photo/'),
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='Male', max_length=10),
        ),
    ]

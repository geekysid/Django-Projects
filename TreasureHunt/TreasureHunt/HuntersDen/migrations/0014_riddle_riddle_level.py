# Generated by Django 3.0.1 on 2020-03-29 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HuntersDen', '0013_auto_20200329_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='riddle',
            name='riddle_level',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='HuntersDen.RiddleLevel'),
            preserve_default=False,
        ),
    ]
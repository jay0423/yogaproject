# Generated by Django 3.0.5 on 2020-08-01 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yogaapp', '0023_notemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='notemodel',
            name='num',
            field=models.IntegerField(default=0, verbose_name='ナンバー'),
        ),
    ]
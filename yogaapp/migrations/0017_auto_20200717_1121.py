# Generated by Django 3.0.5 on 2020-07-17 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yogaapp', '0016_settingplanmodel_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planmodel',
            name='number_of_people',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='プランの予約人数'),
        ),
    ]

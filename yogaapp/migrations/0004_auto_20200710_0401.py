# Generated by Django 3.0.5 on 2020-07-10 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yogaapp', '0003_planmodel_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='planmodel',
            name='plan2',
            field=models.CharField(default=0, max_length=30, verbose_name='プラン2'),
        ),
        migrations.AlterField(
            model_name='planmodel',
            name='month',
            field=models.CharField(default=0, max_length=2, verbose_name='月'),
        ),
    ]

# Generated by Django 3.2.12 on 2022-04-26 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminoo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='card',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='学生学号'),
        ),
    ]

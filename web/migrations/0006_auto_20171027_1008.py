# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-27 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20171027_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='ctime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

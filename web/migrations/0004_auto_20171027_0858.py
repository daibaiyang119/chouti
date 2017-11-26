# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-27 08:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20161221_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('up', models.IntegerField(default=0)),
                ('down', models.IntegerField(default=0)),
                ('ctime', models.DateTimeField()),
                ('device', models.CharField(max_length=16)),
                ('content', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Favor',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('ctime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=32)),
                ('url', models.CharField(max_length=128)),
                ('content', models.CharField(max_length=50)),
                ('faver_count', models.IntegerField(default=0)),
                ('comment_count', models.IntegerField(default=0)),
                ('ctime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='NewsType',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('caption', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='news',
            name='news_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.NewsType'),
        ),
        migrations.AddField(
            model_name='news',
            name='user_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.UserInfo'),
        ),
        migrations.AddField(
            model_name='favor',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.News'),
        ),
        migrations.AddField(
            model_name='favor',
            name='user_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.UserInfo'),
        ),
        migrations.AddField(
            model_name='comment',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.News'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.Comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.UserInfo'),
        ),
        migrations.AlterUniqueTogether(
            name='favor',
            unique_together=set([('user_info', 'news')]),
        ),
    ]

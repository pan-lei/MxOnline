# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-20 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_course_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.CharField(blank=True, default='\u540e\u7aef\u5f00\u53d1', max_length=20, null=True, verbose_name='\u8bfe\u7a0b\u7c7b\u522b'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-21 11:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_auto_20170221_1124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='character',
        ),
    ]

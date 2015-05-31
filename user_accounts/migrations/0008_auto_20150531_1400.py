# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0007_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='facebook_id',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fb_id',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
# Generated by Django 5.1 on 2024-08-19 10:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_appuser_group_is'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appuser',
            name='group_is',
        ),
        migrations.AlterField(
            model_name='appuser',
            name='designation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.designation'),
        ),
    ]

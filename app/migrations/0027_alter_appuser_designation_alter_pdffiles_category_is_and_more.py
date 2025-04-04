# Generated by Django 5.1 on 2024-08-22 05:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_remove_appuser_group_is_alter_appuser_designation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='designation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.designation'),
        ),
        migrations.AlterField(
            model_name='pdffiles',
            name='category_is',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.category'),
        ),
        migrations.AlterField(
            model_name='pdffiles',
            name='group_is',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.group'),
        ),
    ]

# Generated by Django 5.1 on 2024-08-14 12:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_category_sub_parent_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='subchild_parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subchild_parent_categories', to='app.category'),
        ),
    ]

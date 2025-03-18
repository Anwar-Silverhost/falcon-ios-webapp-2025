# Generated by Django 5.1 on 2024-08-14 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_remove_category_sub_parent_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='sub_parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_children_categories', to='app.category'),
        ),
    ]

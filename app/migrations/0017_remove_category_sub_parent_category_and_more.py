# Generated by Django 5.1 on 2024-08-15 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_category_subchild_parent_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='sub_parent_category',
        ),
        migrations.RemoveField(
            model_name='category',
            name='subchild_parent_category',
        ),
    ]

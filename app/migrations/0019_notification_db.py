# Generated by Django 5.1 on 2024-08-19 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_pdffiles'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification_db',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='1', max_length=10)),
            ],
        ),
    ]

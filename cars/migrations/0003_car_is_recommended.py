# Generated by Django 5.2 on 2025-04-15 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='is_recommended',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.2 on 2025-04-17 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('completed', 'Zrealizowane'), ('in_progress', 'W trakcie'), ('not_completed', 'Niezrealizowane')], default='in_progress', max_length=20),
        ),
    ]

# Generated by Django 5.2.1 on 2025-06-28 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_account_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='acc_num',
            field=models.BigAutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]

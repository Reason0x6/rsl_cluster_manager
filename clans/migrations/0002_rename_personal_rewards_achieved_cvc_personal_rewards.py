# Generated by Django 4.2.21 on 2025-05-24 05:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clans', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cvc',
            old_name='personal_rewards_achieved',
            new_name='personal_rewards',
        ),
    ]

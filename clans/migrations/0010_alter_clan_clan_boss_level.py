# Generated by Django 4.2.21 on 2025-05-25 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clans', '0009_alter_player_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clan',
            name='clan_boss_level',
            field=models.CharField(default='[]', help_text='Clan Boss levels down', max_length=255),
        ),
    ]

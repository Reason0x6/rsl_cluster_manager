# Generated by Django 4.2.21 on 2025-05-24 12:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clans', '0006_alter_clan_chimera_clash_required_score_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siege',
            name='opponent',
        ),
        migrations.RemoveField(
            model_name='siege',
            name='opponent_score',
        ),
        migrations.RemoveField(
            model_name='siege',
            name='outcome_win',
        ),
        migrations.RemoveField(
            model_name='siege',
            name='score',
        ),
        migrations.RemoveField(
            model_name='siege',
            name='tier',
        ),
        migrations.AddField(
            model_name='siege',
            name='points',
            field=models.PositiveIntegerField(default=0, help_text='Total points earned in the Siege'),
        ),
        migrations.AddField(
            model_name='siege',
            name='position',
            field=models.PositiveIntegerField(default=0, help_text='Final position in the Siege'),
        ),
        migrations.AlterField(
            model_name='siege',
            name='date_recorded',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='When this Siege occurred'),
        ),
    ]

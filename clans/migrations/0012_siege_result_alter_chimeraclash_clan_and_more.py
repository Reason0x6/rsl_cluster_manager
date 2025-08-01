# Generated by Django 4.2.21 on 2025-05-25 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clans', '0011_hydrarecord_cvcrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='siege',
            name='result',
            field=models.CharField(choices=[('win', 'Win'), ('loss', 'Loss')], default='loss', max_length=10),
        ),
        migrations.AlterField(
            model_name='chimeraclash',
            name='clan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chimera_records', to='clans.clan'),
        ),
        migrations.AlterField(
            model_name='siege',
            name='clan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='siege_records', to='clans.clan'),
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-17 03:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_alter_playerstats_accuracy'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='playerstats',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='game_winner', to='games.team'),
        ),
        migrations.AddField(
            model_name='playerstats',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
    ]

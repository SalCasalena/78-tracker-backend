# Generated by Django 5.1.7 on 2025-03-17 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_rename_game_state_game_cups'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerstats',
            name='own_cups',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_game_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='game',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='primary_teams',
                to='teams.game',
                help_text='Primary game this team competes in'
            ),
        ),
        migrations.AddField(
            model_name='team',
            name='looking_for_players',
            field=models.BooleanField(
                default=False,
                help_text='Whether the team is actively looking for new players'
            ),
        ),
    ]

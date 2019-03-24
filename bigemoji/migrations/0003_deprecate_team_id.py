from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('bigemoji', '0002_bigemojialias_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bigemoji',
            old_name='team_id',
            new_name='team_id_deprecated'
        ),
        migrations.AddField(
            model_name='bigemoji',
            name='team',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, to='slack.SlackTeam'),
        ),
    ]

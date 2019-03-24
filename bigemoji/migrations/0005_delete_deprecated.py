from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigemoji', '0004_copy_team_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bigemoji',
            unique_together={('team', 'emoji_name')},
        ),
        migrations.RemoveField(
            model_name='bigemoji',
            name='team_id_deprecated'
        ),
        migrations.AlterField(
            model_name='bigemoji',
            name='team',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='slack.SlackTeam', default='(CHANGEME)'),
            preserve_default=False
        ),
        migrations.AlterField(
            model_name='bigemojialias',
            name='team',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='slack.SlackTeam', default='(CHANGEME)'),
            preserve_default=False
        ),
    ]

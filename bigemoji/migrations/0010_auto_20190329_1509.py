from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bigemoji', '0009_bigemojistorage'),
        ('slack', '0008_move_slack_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bigemoji',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slackauth.SlackAccount'),
        ),
        migrations.AlterField(
            model_name='bigemoji',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slackauth.SlackTeam'),
        ),
        migrations.AlterField(
            model_name='bigemojialias',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slackauth.SlackAccount'),
        ),
        migrations.AlterField(
            model_name='bigemojialias',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slackauth.SlackTeam'),
        ),
    ]

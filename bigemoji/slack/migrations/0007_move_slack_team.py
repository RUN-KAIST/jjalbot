from django.db import migrations, transaction


def copy_slack_team(apps, schema_editor):
    SlackTeamDeprecated = apps.get_model('slack', 'SlackTeam')
    SlackTeam = apps.get_model('slackauth', 'SlackTeam')
    BigEmojiStorage = apps.get_model('bigemoji', 'BigEmojiStorage')

    with transaction.atomic():
        for row_deprecated in SlackTeamDeprecated.objects.all():
            row_team = SlackTeam(
                id=row_deprecated.id,
                name=row_deprecated.name,
                domain=row_deprecated.domain,
                verified=row_deprecated.verified,
                extra_data=row_deprecated.extra_data,
                date_created=row_deprecated.date_created,
            )
            row_team.save()

            row_storage = BigEmojiStorage(
                team=row_team,
                max_size=row_deprecated.max_size,
                delete_eta=row_deprecated.delete_eta,
            )
            row_storage.save()


def reverse_copy_slack_team(apps, schema_editor):
    SlackTeamDeprecated = apps.get_model('slack', 'SlackTeam')
    SlackTeam = apps.get_model('slackauth', 'SlackTeam')

    with transaction.atomic():
        for row_deprecated in SlackTeamDeprecated.objects.all():
            row_team = SlackTeam.objects.get(id=row_deprecated.id)
            row_team.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('slack', '0006_move_slack_token'),
        ('slackauth', '0001_initial'),
        ('bigemoji', '0009_bigemojistorage')
    ]

    operations = [
        migrations.RunPython(
            copy_slack_team,
            reverse_copy_slack_team
        )
    ]

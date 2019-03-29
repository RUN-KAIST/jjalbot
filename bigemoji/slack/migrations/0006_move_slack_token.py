from django.db import migrations, transaction


def copy_slack_account(apps, schema_editor):
    SlackTokenDeprecated = apps.get_model('slack', 'SlackTokenDeprecated')
    SlackToken = apps.get_model('slackauth', 'SlackToken')

    with transaction.atomic():
        for row_deprecated in SlackTokenDeprecated.objects.all():
            row = SlackToken(
                token=row_deprecated.token,
                token_secret=row_deprecated.token_secret,
                expires_at=row_deprecated.expires_at,
                scopes=row_deprecated.scopes,
                date_created=row_deprecated.date_created,
                account=row_deprecated.account,
                app=row_deprecated.app
            )
            row.save()


def reverse_copy_slack_account(apps, schema_editor):
    SlackTokenDeprecated = apps.get_model('slack', 'SlackTokenDeprecated')
    SlackToken = apps.get_model('slackauth', 'SlackToken')

    with transaction.atomic():
        for row_deprecated in SlackTokenDeprecated.objects.all():
            row = SlackToken.objects.get(
                app=row_deprecated.app,
                account=row_deprecated.account,
                scopes=row_deprecated.scopes
            )
            row.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('slack', '0005_auto_20190329_1408'),
        ('slackauth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            copy_slack_account,
            reverse_copy_slack_account
        )
    ]

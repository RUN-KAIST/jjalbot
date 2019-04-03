from django.db import migrations, transaction


def copy_slack_token(apps, schema_editor):
    SlackToken = apps.get_model('slackauth', 'SlackToken')
    SlackUserToken = apps.get_model('slackauth', 'SlackUserToken')
    SlackBotToken = apps.get_model('slackauth', 'SlackBotToken')
    with transaction.atomic():
        for row in SlackToken.objects.all():
            if row.token_type == 0:
                SlackUserToken(
                    token=row.token,
                    extra_data=row.extra_data,
                    date_created=row.date_created,
                    scope=row.scope,
                    account=row.account,
                    app=row.app
                ).save()
            elif row.token_type == 1:
                SlackBotToken(
                    token=row.token,
                    extra_data=row.extra_data,
                    date_created=row.date_created,
                    slack_bot_id=row.extra_data.get('bot_user_id'),
                    app=row.app,
                    team=row.account.team
                ).save()


def reverse_copy_slack_token(apps, schema_editor):
    SlackToken = apps.get_model('slackauth', 'SlackToken')
    SlackUserToken = apps.get_model('slackauth', 'SlackUserToken')
    SlackBotToken = apps.get_model('slackauth', 'SlackBotToken')
    with transaction.atomic():
        for row in SlackToken.objects.all():
            if row.token_type == 0:
                SlackUserToken.objects.filter(
                    account=row.account,
                    app=row.app
                ).delete()
            elif row.token_type == 1:
                SlackBotToken.objects.filter(
                    app=row.app,
                    team=row.account.team
                ).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('slackauth', '0012_auto_20190403_1540'),
    ]

    operations = [
        migrations.RunPython(
            copy_slack_token,
            reverse_copy_slack_token
        )
    ]

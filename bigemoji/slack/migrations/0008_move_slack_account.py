from django.db import migrations, transaction


def copy_slack_account(apps, schema_editor):
    SlackAccountDeprecated = apps.get_model("slack", "SlackAccountDeprecated")
    SlackAccount = apps.get_model("slackauth", "SlackAccount")
    SlackTeam = apps.get_model("slackauth", "SlackTeam")

    with transaction.atomic():
        for row_deprecated in SlackAccountDeprecated.objects.all():
            row = SlackAccount(
                account=row_deprecated.account,
                slack_user_id=row_deprecated.slack_user_id,
                extra_data=row_deprecated.extra_data,
                team=SlackTeam.objects.get(id=row_deprecated.team.id),
                date_created=row_deprecated.date_created,
            )
            row.save()


def reverse_copy_slack_account(apps, schema_editor):
    SlackAccountDeprecated = apps.get_model("slack", "SlackAccountDeprecated")
    SlackAccount = apps.get_model("slackauth", "SlackAccount")
    SlackTeam = apps.get_model("slackauth", "SlackTeam")

    with transaction.atomic():
        for row_deprecated in SlackAccountDeprecated.objects.all():
            row = SlackAccount.objects.get(
                team=SlackTeam.objects.get(id=row_deprecated.team.id),
                slack_user_id=row_deprecated.slack_user_id,
            )
            row.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("slack", "0007_move_slack_team"), ("slackauth", "0001_initial")]

    operations = [migrations.RunPython(copy_slack_account, reverse_copy_slack_account)]

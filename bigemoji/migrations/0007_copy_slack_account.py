from django.db import migrations, transaction


def copy_slack_account(apps, schema_editor):
    BigEmoji = apps.get_model("bigemoji", "BigEmoji")
    while BigEmoji.objects.filter(owner__isnull=True).exists():
        with transaction.atomic():
            for row in BigEmoji.objects.filter(owner__isnull=True):
                row.owner = row.author.slackaccount
                row.save()


def reverse_copy_slack_account(apps, schema_editor):
    BigEmoji = apps.get_model("bigemoji", "BigEmoji")
    while BigEmoji.objects.filter(owner__isnull=False).exists():
        with transaction.atomic():
            for row in BigEmoji.objects.filter(owner__isnull=False):
                row.owner = None
                row.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("bigemoji", "0006_add_owner")]

    operations = [migrations.RunPython(copy_slack_account, reverse_copy_slack_account)]

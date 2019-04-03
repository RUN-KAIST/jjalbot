from django.db import migrations, transaction
from django.db.models import Max


def modify_slack_token(apps, schema_editor):
    SlackToken = apps.get_model("slackauth", "SlackToken")
    with transaction.atomic():
        for row in SlackToken.objects.values("app", "account", "token").distinct():
            app = row["app"]
            account = row["account"]
            token = row["token"]
            last_created = SlackToken.objects.filter(
                app=app, account=account, token=token
            ).aggregate(Max("date_created"))["date_created__max"]
            SlackToken.objects.filter(app=app, account=account, token=token).exclude(
                date_created=last_created
            ).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("slackauth", "0009_auto_20190403_1431")]

    operations = [migrations.RunPython(modify_slack_token)]

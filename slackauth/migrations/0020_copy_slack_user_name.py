from django.db import migrations, transaction


def copy_slack_user_name(apps, schema_editor):
    SlackAccount = apps.get_model('slackauth', 'SlackAccount')
    with transaction.atomic():
        for row in SlackAccount.objects.all():
            row.name = row.extra_data.get('name', 'NONAME')
            row.save()


def reverse_copy_slack_user_name(apps, schema_editor):
    SlackAccount = apps.get_model('slackauth', 'SlackAccount')
    with transaction.atomic():
        for row in SlackAccount.objects.all():
            row.name = 'NONAME'


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('slackauth', '0019_slackaccount_name'),
    ]

    operations = [
        migrations.RunPython(
            copy_slack_user_name,
            reverse_copy_slack_user_name
        )
    ]

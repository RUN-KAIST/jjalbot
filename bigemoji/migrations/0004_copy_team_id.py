from django.db import migrations, transaction


def copy_team_id(apps, schema_editor):
    BigEmoji = apps.get_model('bigemoji', 'BigEmoji')
    SlackTeam = apps.get_model('slack', 'SlackTeam')
    while BigEmoji.objects.filter(team__isnull=True).exists():
        with transaction.atomic():
            for row in BigEmoji.objects.filter(team__isnull=True):
                row.team = SlackTeam.objects.get(id=row.team_id_deprecated)
                row.save()


def reverse_copy_team_id(apps, schema_editor):
    BigEmoji = apps.get_model('bigemoji', 'BigEmoji')
    while BigEmoji.objects.filter(team__isnull=False).exists():
        with transaction.atomic():
            for row in BigEmoji.objects.filter(team__isnull=False):
                row.team = None
                row.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('bigemoji', '0003_deprecate_team_id'),
        ('slack', '0002_auto_20190323_1741')
    ]

    operations = [
        migrations.RunPython(
            copy_team_id,
            reverse_copy_team_id
        )
    ]

from django.db import migrations, transaction


def copy_team_storage(apps, schema_editor):
    BigEmoji = apps.get_model("bigemoji", "BigEmoji")
    with transaction.atomic():
        for row in BigEmoji.objects.filter(storage__isnull=True):
            row.storage = row.team.bigemojistorage
            row.save()


def reverse_copy_team_storage(apps, schema_editor):
    BigEmoji = apps.get_model("bigemoji", "BigEmoji")
    with transaction.atomic():
        for row in BigEmoji.objects.filter(storage__isnull=False):
            row.storage = None
            row.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("bigemoji", "0015_bigemoji_storage")]

    operations = [migrations.RunPython(copy_team_storage, reverse_copy_team_storage)]

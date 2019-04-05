from django.db import migrations, transaction


def set_storage_size(apps, schema_editor):
    BigEmojiStorage = apps.get_model('bigemoji', 'BigEmojiStorage')
    BigEmoji = apps.get_model('bigemoji', 'BigEmoji')
    with transaction.atomic():
        for row in BigEmojiStorage.objects.all():
            for bigemoji in BigEmoji.objects.filter(storage=row):
                if bigemoji.alias is None:
                    row.occupied += bigemoji.image_file.size
                row.entries += 1
            row.save()


def reverse_set_storage_size(apps, schema_editor):
    BigEmojiStorage = apps.get_model('bigemoji', 'BigEmojiStorage')
    with transaction.atomic():
        for row in BigEmojiStorage.objects.all():
            row.occupied = 0
            row.entries = 0
            row.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('bigemoji', '0019_auto_20190404_1640'),
    ]

    operations = [
        migrations.RunPython(
            set_storage_size,
            reverse_set_storage_size
        )
    ]

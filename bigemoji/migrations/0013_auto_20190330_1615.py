from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("bigemoji", "0012_auto_20190330_1556")]

    operations = [
        migrations.RenameField(
            model_name="bigemoji", old_name="image", new_name="image_file"
        )
    ]

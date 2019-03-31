from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigemoji', '0016_copy_team_storage'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bigemoji',
            unique_together={('storage', 'emoji_name')},
        ),
        migrations.RemoveField(
            model_name='bigemoji',
            name='team'
        ),
        migrations.AlterField(
            model_name='bigemoji',
            name='storage',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='bigemoji.BigEmojiStorage', default=-1),
            preserve_default=False
        ),
    ]

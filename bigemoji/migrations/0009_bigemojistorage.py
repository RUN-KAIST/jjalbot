from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("slackauth", "0001_initial"),
        ("bigemoji", "0008_deprecate_author"),
    ]

    operations = [
        migrations.CreateModel(
            name="BigEmojiStorage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("max_size", models.IntegerField(default=10000000)),
                ("delete_eta", models.IntegerField(default=3600)),
                (
                    "team",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="slackauth.SlackTeam",
                    ),
                ),
            ],
        )
    ]

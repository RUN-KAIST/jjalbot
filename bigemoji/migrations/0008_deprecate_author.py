from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("bigemoji", "0007_copy_slack_account")]

    operations = [
        migrations.RemoveField(model_name="bigemoji", name="author"),
        migrations.AlterField(
            model_name="bigemoji",
            name="owner",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="slack.SlackAccount", default=-1
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(model_name="bigemojialias", name="author"),
        migrations.AlterField(
            model_name="bigemojialias",
            name="owner",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="slack.SlackAccount", default=-1
            ),
            preserve_default=False,
        ),
    ]

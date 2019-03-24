from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('bigemoji', '0005_delete_deprecated'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigemoji',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, to='slack.SlackAccount'),
        ),
        migrations.AddField(
            model_name='bigemojialias',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, to='slack.SlackAccount'),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0002_auto_20190323_1741'),
        ('bigemoji', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigemojialias',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='slack.SlackTeam'),
        ),
        migrations.AlterUniqueTogether(
            name='bigemojialias',
            unique_together={('team', 'alias_name')},
        ),
    ]

# Generated by Django 2.1.7 on 2019-04-02 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
        ('slackauth', '0002_slacktoken_token_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='slacktoken',
            unique_together={('app', 'account', 'token_type', 'scopes')},
        ),
    ]

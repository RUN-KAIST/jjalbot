# Generated by Django 2.1.7 on 2019-04-04 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slackauth', '0016_auto_20190403_1652'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slackusertoken',
            options={'verbose_name': 'slack user token', 'verbose_name_plural': 'slack user tokens'},
        ),
    ]

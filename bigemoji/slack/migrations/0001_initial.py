# Generated by Django 2.1.7 on 2019-03-13 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(verbose_name='token')),
                ('token_secret', models.TextField(blank=True, verbose_name='token secret')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires at')),
                ('scopes', models.TextField(verbose_name='scopes')),
                ('date_created', models.DateTimeField(auto_now=True, verbose_name='date created')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialaccount.SocialAccount')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialaccount.SocialApp')),
            ],
            options={
                'verbose_name': 'slack application token',
                'verbose_name_plural': 'slack application tokens',
            },
        ),
        migrations.AlterUniqueTogether(
            name='slacktoken',
            unique_together={('app', 'account', 'scopes')},
        ),
    ]
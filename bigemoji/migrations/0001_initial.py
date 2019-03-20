# Generated by Django 2.1.7 on 2019-03-10 07:21

import bigemoji.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.CreateModel(
            name='BigEmoji',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.CharField(max_length=10)),
                ('emoji_name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to=bigemoji.models.team_directory)),
                ('date_created', models.DateTimeField(auto_now=True, verbose_name='date created')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialaccount.SocialAccount')),
            ],
        ),
        migrations.CreateModel(
            name='BigEmojiAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias_name', models.CharField(max_length=100)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialaccount.SocialAccount')),
                ('bigemoji', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigemoji.BigEmoji')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bigemoji',
            unique_together={('team_id', 'emoji_name')},
        ),
    ]
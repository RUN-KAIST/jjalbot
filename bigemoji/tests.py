from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from PIL import Image
from io import BytesIO
import os
import shutil
import six

from slackauth.tests import SlackTestCase, SlackClient

from .models import BigEmoji


class BigEmojiBasicTest(SlackTestCase):
    def test_index(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )
        resp = self.client.get(reverse('bigemoji:index'))
        self.assertRedirects(
            resp,
            reverse('bigemoji:bigemoji', kwargs={
                'team_id': team_id,
                'slack_user_id': slack_user_id
            })
        )

    def test_access_other_team(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'
        other_team_id = 'T0G9PQBBL'
        other_user_id = 'U0G9QF9C7'

        self.client.slack_login(
            team_name='test',
            team_id=other_team_id,
            user_name='test',
            user_id=other_user_id
        )
        self.client.logout()
        self.client.slack_login(
            team_name='test2',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )
        resp = self.client.get(reverse('bigemoji:bigemoji', kwargs={
            'team_id': other_team_id,
            'slack_user_id': other_user_id
        }))
        self.assertEqual(resp.status_code, 404)

    def test_access_other_user(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'
        other_user_id = 'U0G9QF9C7'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=other_user_id
        )
        self.client.logout()
        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )
        resp = self.client.get(reverse('bigemoji:bigemoji', kwargs={
            'team_id': team_id,
            'slack_user_id': other_user_id
        }))
        self.assertEqual(resp.status_code, 404)


def create_png(name, r=0, g=0, b=0):
    file = BytesIO()
    image = Image.new('RGBA', size=(50, 50), color=(r, g, b))
    image.save(file, 'png')
    file.name = '{}.png'.format(name)
    file.seek(0)
    return file


class BigEmojiClient(SlackClient):
    def add_emoji(self, team_id, slack_user_id, emoji_name, image_file):
        return self.post(
            reverse('bigemoji:add', kwargs={
                'team_id': team_id,
                'slack_user_id': slack_user_id
            }),
            data={
                'emoji_name': emoji_name,
                'image_file': image_file
            },
            follow=True
        )

    def add_alias(self, team_id, slack_user_id, emoji_name, bigemoji):
        if isinstance(bigemoji, six.string_types):
            bigemoji = BigEmoji.objects.get(storage__team_id=team_id, emoji_name=bigemoji)

        return self.post(
            reverse('bigemoji:alias', kwargs={
                'team_id': team_id,
                'slack_user_id': slack_user_id
            }),
            data={
                'emoji_name': emoji_name,
                'alias': bigemoji.pk
            }
        )

    def remove_emoji(self, team_id, slack_user_id, emoji_name):
        return self.post(
            reverse('bigemoji:remove', kwargs={
                'team_id': team_id,
                'slack_user_id': slack_user_id,
                'bigemoji_name': emoji_name
            })
        )


class BigEmojiTestCase(SlackTestCase):
    def setUp(self):
        os.mkdir(settings.MEDIA_ROOT)
        super(BigEmojiTestCase, self).setUp()
        self.client = BigEmojiClient()

    def tearDown(self):
        super(BigEmojiTestCase, self).tearDown()
        shutil.rmtree(settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test_media'))
class BigEmojiFunctionTest(BigEmojiTestCase):
    def test_add(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )

        img = create_png('test')

        self.client.get(reverse('bigemoji:index'), follow=True)
        resp = self.client.add_emoji(team_id, slack_user_id, 'test', img)
        self.assertRedirects(resp, reverse('bigemoji:bigemoji', kwargs={
            'team_id': team_id,
            'slack_user_id': slack_user_id
        }))
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')

    def test_alias(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )

        img = create_png('test')

        self.client.get(reverse('bigemoji:index'), follow=True)
        self.client.add_emoji(team_id, slack_user_id, 'test', img)
        test_emoji = BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')
        self.client.add_alias(team_id, slack_user_id, 'alias', test_emoji)
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='alias')

    def test_remove(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )

        img = create_png('test')

        self.client.get(reverse('bigemoji:index'), follow=True)
        self.client.add_emoji(team_id, slack_user_id, 'test', img)
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')
        self.client.remove_emoji(team_id, slack_user_id, 'test')
        with self.assertRaises(BigEmoji.DoesNotExist):
            BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')

    def test_remove_alias(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )

        img = create_png('test')

        self.client.get(reverse('bigemoji:index'), follow=True)
        self.client.add_emoji(team_id, slack_user_id, 'test', img)
        test_emoji = BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')
        self.client.add_alias(team_id, slack_user_id, 'alias', test_emoji)
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='alias')
        self.client.remove_emoji(team_id, slack_user_id, 'alias')
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')
        with self.assertRaises(BigEmoji.DoesNotExist):
            BigEmoji.objects.get(storage__team_id=team_id, emoji_name='alias')

    def test_remove_emoji_and_alias(self):
        team_id = 'T0G9PQBBK'
        slack_user_id = 'U0G9QF9C6'

        self.client.slack_login(
            team_name='test',
            team_id=team_id,
            user_name='test',
            user_id=slack_user_id
        )

        img = create_png('test')

        self.client.get(reverse('bigemoji:index'), follow=True)
        self.client.add_emoji(team_id, slack_user_id, 'test', img)
        test_emoji = BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')
        self.client.add_alias(team_id, slack_user_id, 'alias', test_emoji)
        BigEmoji.objects.get(storage__team_id=team_id, emoji_name='alias')
        self.client.remove_emoji(team_id, slack_user_id, 'test')

        with self.assertRaises(BigEmoji.DoesNotExist):
            BigEmoji.objects.get(storage__team_id=team_id, emoji_name='alias')
        with self.assertRaises(BigEmoji.DoesNotExist):
            BigEmoji.objects.get(storage__team_id=team_id, emoji_name='test')

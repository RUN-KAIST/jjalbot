from django.conf import settings
from django.test import TestCase, Client
from django.contrib.sites.models import Site
from django.urls import reverse

from allauth.tests import MockedResponse, mocked_response
from allauth.socialaccount.models import SocialApp

import json
from urllib.parse import urlparse, parse_qs

from .models import SlackAccount, SlackTeam, SlackUserToken
from .views import SlackOAuth2Adapter


def generate_access_token(team_id, user_id, bot=False):
    token_prefix = 'xoxb' if bot else 'xoxp'
    token_list = [token_prefix]
    for key_id in [team_id, user_id]:
        token_val = ''
        for c in key_id:
            tok_str = str(ord(c))
            token_val += str(len(tok_str)) + tok_str
        token_list.append(token_val)
    return '-'.join(token_list)


class SlackClient(Client):
    def slack_login(self, team_name, team_id, user_name, user_id, scope=None, process='login'):
        if scope is None:
            scope = settings.SLACK_LOGIN_SCOPE

        access_token_resp = MockedResponse(
            200,
            json.dumps(
                {
                    'access_token': generate_access_token(team_id, user_id),
                    'scope': scope,
                }
            ),
            {
                'content-type': 'text/json',
            }
        )
        user_info_resp = MockedResponse(
            200,
            json.dumps(
                {
                    "ok": True,
                    "user": {
                        "name": user_name,
                        "id": user_id,
                        "email": "{}@example.com".format('_'.join(user_name.split())),
                    },
                    "team": {
                        "name": team_name,
                        "domain": '-'.join(team_name.split()),
                        "id": team_id,
                    }
                }
            ),
            {
                'content-type': 'text/json',
            }
        )
        resp = self.get(reverse('slack_login'), {
            'next': settings.LOGIN_REDIRECT_URL,
            'process': process,
            'scope': scope,
        })
        if resp.status_code != 302:
            return False

        parsed_url = urlparse(resp.url)
        redirect_url = '{}://{}{}'.format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)
        if redirect_url != SlackOAuth2Adapter.authorize_url:
            return False

        query = parse_qs(parsed_url.query)
        if 'state' not in query or len(query['state']) != 1:
            return False

        state = query['state'][0]
        with mocked_response(access_token_resp, user_info_resp):
            resp = self.get(reverse('slack_callback'), {'code': '123', 'state': state})

        if resp.status_code != 302:
            return False

        return True


class SlackTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.app = SocialApp.objects.create(
            provider='slack',
            name='test app',
            client_id='123456789.987654321',
            secret='1234567890abcdef',
        )
        cls.app.sites.add(Site.objects.get_current())

    def setUp(self):
        super(SlackTestCase, self).setUp()
        self.client = SlackClient()


class SlackLoginTest(SlackTestCase):
    def test_login(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.assertEqual(SlackTeam.objects.filter(id='T0G9PQBBK').count(), 1)

        team = SlackTeam.objects.get(id='T0G9PQBBK')
        self.assertEqual(SlackAccount.objects.filter(team=team, slack_user_id='U0G9QF9C6').count(), 1)

        account = SlackAccount.objects.get(team=team, slack_user_id='U0G9QF9C6')
        self.assertGreaterEqual(SlackUserToken.objects.filter(slack_account=account).count(), 1)

    def test_duplicate_team(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.client.logout()
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test2',
            user_id='U0G9QF9C7'
        ))

    def test_duplicate_user_name(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.client.logout()
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C7'
        ))

    def test_duplicate_user_id(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.client.logout()
        self.assertTrue(self.client.slack_login(
            team_name='test2',
            team_id='T1G9PQBBK',
            user_name='test2',
            user_id='U0G9QF9C6'
        ))

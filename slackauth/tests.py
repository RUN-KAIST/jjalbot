from django.conf import settings
from django.test import TestCase, Client
from django.contrib.sites.models import Site
from django.urls import reverse

from allauth.tests import MockedResponse, mocked_response
from allauth.socialaccount.models import SocialApp, SocialAccount

import json
import random
import string
from urllib.parse import urlparse, parse_qs

from .models import SlackAccount, SlackTeam, SlackUserToken
from .views import SlackOAuth2Adapter
from .provider import SlackProvider


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


def _generate_id(id_type):
    return id_type + ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))


def generate_team_id():
    return _generate_id('T')


def generate_user_id():
    return _generate_id('U')


def generate_bot_id():
    return _generate_id('B')


class SlackClient(Client):
    def _slack_login(self, team_name, team_id, user_name, user_id,
                     scope=None, process='login', next_url=None, **kwargs):
        if scope is None:
            scope = settings.SLACK_LOGIN_SCOPE

        if next_url is None:
            next_url = settings.LOGIN_REDIRECT_URL

        scope_list = scope.split(',')
        try:
            app = SocialApp.objects.get_current(SlackProvider.id)
            account = SlackAccount.objects.get(team_id=team_id, slack_user_id=user_id)
            current_scope_list = SlackUserToken.objects.get(app=app, slack_account=account).scope.split(',')
        except (SlackAccount.DoesNotExist, SlackUserToken.DoesNotExist):
            current_scope_list = []

        current_scope_set = set(current_scope_list)
        full_scope_list = []
        for sc in scope_list:
            if sc not in current_scope_set:
                full_scope_list.append(sc)
        full_scope_list.extend(current_scope_list)
        full_scope = ','.join(full_scope_list)

        access_token = {
            'access_token': generate_access_token(team_id, user_id),
            'scope': full_scope,
        }
        if 'bot' in full_scope_list:
            access_token['bot'] = {
                'bot_user_id': kwargs['bot_user_id'],
                'bot_access_token': generate_access_token(team_id, user_id, bot=True)
            }
        access_token_resp = MockedResponse(
            200,
            json.dumps(access_token),
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
                        "email": "{}_{}@example.com".format('_'.join(user_name.split()), user_id),
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
            'next': next_url,
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

        if resp.status_code != 302 or resp.url != next_url:
            return False

        return True

    def slack_login(self, team_name, team_id, user_name, user_id):
        return self._slack_login(team_name, team_id, user_name, user_id)

    def slack_connect(self, team_name, team_id, user_name, user_id):
        return self._slack_login(team_name, team_id, user_name, user_id, process='connect')

    def slack_install(self, account, bot_user_id):
        return self._slack_login(
            account.team.name,
            account.team.id,
            account.name,
            account.slack_user_id,
            scope='identify,bot,commands',
            process='redirect',
            bot_user_id=bot_user_id
        )


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
        self.assertEqual(SlackUserToken.objects.filter(slack_account=account).count(), 1)

    def test_logout(self):
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
            user_id='U0G9QF9C6'
        ))
        self.assertEqual(SlackAccount.objects.all().count(), 1)

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
        self.assertEqual(SlackAccount.objects.all().count(), 2)

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
        self.assertEqual(SlackAccount.objects.all().count(), 2)

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
        self.assertEqual(SlackAccount.objects.all().count(), 2)

    def test_many_ids(self):
        team_ids = [generate_team_id() for _ in range(random.randint(5, 10))]
        total_team = len(team_ids)
        total_user = 0
        for team_id in team_ids:
            user_ids = [generate_user_id() for _ in range(random.randint(5, 10))]
            for user_id in user_ids:
                self.assertTrue(self.client.slack_login(
                    team_name=team_id,
                    team_id=team_id,
                    user_name=user_id,
                    user_id=user_id,
                ))
                self.client.logout()
            total_user += len(user_ids)
        self.assertEqual(SlackTeam.objects.all().count(), total_team)
        self.assertEqual(SlackAccount.objects.all().count(), total_user)


class SlackConnectTest(SlackTestCase):
    def test_connect(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.assertTrue(self.client.slack_connect(
            team_name='test2',
            team_id='T0G9PQBBL',
            user_name='test',
            user_id='U0G9QF9C7'
        ))
        account = SlackAccount.objects.get(team_id='T0G9PQBBK', slack_user_id='U0G9QF9C6').account
        user = account.user
        self.assertEqual(SocialAccount.objects.filter(user=user).count(), 2)

    def test_duplicate_connect(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.assertTrue(self.client.slack_connect(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        account = SlackAccount.objects.get(team_id='T0G9PQBBK', slack_user_id='U0G9QF9C6').account
        user = account.user
        self.assertEqual(SocialAccount.objects.filter(user=user).count(), 1)

    def test_already_connected(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        self.client.logout()
        self.assertTrue(self.client.slack_login(
            team_name='test2',
            team_id='T0G9PQBBL',
            user_name='test',
            user_id='U0G9QF9C7'
        ))
        self.assertTrue(self.client.slack_connect(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        account = SlackAccount.objects.get(team_id='T0G9PQBBK', slack_user_id='U0G9QF9C6').account
        user = account.user
        self.assertEqual(SocialAccount.objects.filter(user=user).count(), 1)
        account = SlackAccount.objects.get(team_id='T0G9PQBBL', slack_user_id='U0G9QF9C7').account
        user = account.user
        self.assertEqual(SocialAccount.objects.filter(user=user).count(), 1)


class SlackInstallTest(SlackTestCase):
    def test_install(self):
        self.assertTrue(self.client.slack_login(
            team_name='test',
            team_id='T0G9PQBBK',
            user_name='test',
            user_id='U0G9QF9C6'
        ))
        account = SlackAccount.objects.get(team_id='T0G9PQBBK', slack_user_id='U0G9QF9C6')
        self.assertTrue(self.client.slack_install(account, 'B2RD9LQ27'))

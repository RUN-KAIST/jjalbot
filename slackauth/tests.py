from django.conf import settings
from django.test import TestCase
from django.contrib.sites.models import Site

from allauth.tests import MockedResponse, mocked_response
from allauth.socialaccount.models import SocialApp

import json
from urllib.parse import urlparse, parse_qs

from .models import SlackAccount, SlackTeam, SlackUserToken
from .views import SlackOAuth2Adapter


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


class SlackLoginTest(SlackTestCase):
    def test_login(self):
        resp = self.client.get('/jjalbot/accounts/slack/login/?next=/jjalbot/')
        self.assertEqual(resp.status_code, 302)

        parsed_url = urlparse(resp.url)
        self.assertEqual(
            '{}://{}{}'.format(parsed_url.scheme, parsed_url.netloc, parsed_url.path),
            SlackOAuth2Adapter.authorize_url
        )

        query = parse_qs(parsed_url.query)
        self.assertTrue('state' in query)
        self.assertEqual(len(query['state']), 1)

        state = query['state'][0]

        with mocked_response(
            MockedResponse(
                200,
                json.dumps(
                    {
                        'access_token': 'xoxp-23984754863-2348975623103',
                        'scope': settings.SLACK_LOGIN_SCOPE,
                    }
                ),
                {
                    'content-type': 'text/json',
                }
            ),
            MockedResponse(
                200,
                json.dumps(
                    {
                        "ok": True,
                        "user": {
                            "name": "Sonny Whether",
                            "id": "U0G9QF9C6",
                            "email": "admin@example.com",
                        },
                        "team": {
                            "name": "Captain Fabian's Naval Supply",
                            "domain": "cfns",
                            "id": "T0G9PQBBK",
                        }
                    }
                ),
                {
                    'content-type': 'text/json',
                }
            )
        ):
            resp = self.client.get(
                '/jjalbot/accounts/slack/login/callback/?code=123&state={}'.format(state)
            )
        self.assertRedirects(resp, '/jjalbot/', fetch_redirect_response=False)

        self.assertEqual(SlackTeam.objects.filter(id='T0G9PQBBK').count(), 1)

        team = SlackTeam.objects.get(id='T0G9PQBBK')
        self.assertEqual(SlackAccount.objects.filter(team=team, slack_user_id='U0G9QF9C6').count(), 1)

        account = SlackAccount.objects.get(team=team, slack_user_id='U0G9QF9C6')
        self.assertGreaterEqual(SlackUserToken.objects.filter(slack_account=account).count(), 1)

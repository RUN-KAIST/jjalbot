from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SlackAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("user").get("image_192", None)

    def to_str(self):
        dflt = super(SlackAccount, self).to_str()
        return "%s (%s)" % (self.account.extra_data.get("name", ""), dflt)


class SlackProvider(OAuth2Provider):
    id = "slack"
    name = "Slack"
    account_class = SlackAccount

    def sociallogin_from_response(self, request, response):
        from allauth.socialaccount.models import SocialAccount
        from allauth.socialaccount.adapter import get_adapter

        from .models import SlackLogin

        slack_response = response.get("slack_data")
        adapter = get_adapter(request)
        uid = self.extract_uid(slack_response)
        extra_data = self.extract_extra_data(slack_response)
        common_fields = self.extract_common_fields(slack_response)
        socialaccount = SocialAccount(extra_data=extra_data, uid=uid, provider=self.id)
        email_addresses = self.extract_email_addresses(slack_response)
        self.cleanup_email_addresses(common_fields.get("email"), email_addresses)
        sociallogin = SlackLogin(
            access_token=response.get("access_token"),
            account=socialaccount,
            email_addresses=email_addresses,
        )
        user = sociallogin.user = adapter.new_user(request, sociallogin)
        user.set_unusable_password()
        adapter.populate_user(request, sociallogin, common_fields)
        return sociallogin

    def extract_uid(self, data):
        return "%s_%s" % (
            str(data.get("team").get("id")),
            str(data.get("user").get("id")),
        )

    def extract_common_fields(self, data):
        return dict(name=data.get("name"), email=data.get("user").get("email", None))


provider_classes = [SlackProvider]

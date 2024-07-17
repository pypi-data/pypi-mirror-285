from urllib.parse import urlparse

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from wise.settings.env import SentrySettings


class SentryHandler:
    @staticmethod
    def filter_transactions(event, hint):
        """
        Reference:
            https://docs.sentry.io/platforms/python/guides/django/configuration/filtering/#using-platformidentifier-namebefore-send-transaction-
        :param event:
        :param hint:
        :return:
        """
        url_string = event["request"]["url"]
        parsed_url = urlparse(url_string)

        if parsed_url.path == "/health":
            return None

        return event

    @staticmethod
    def setup_sentry(config: SentrySettings):
        if config.enabled:
            sentry_sdk.init(
                dsn=config.dsn,
                integrations=[
                    DjangoIntegration(),
                ],
                environment=config.environment,
                traces_sample_rate=config.sample_rate,
                send_default_pii=True,
                before_send_transaction=SentryHandler.filter_transactions,
            )

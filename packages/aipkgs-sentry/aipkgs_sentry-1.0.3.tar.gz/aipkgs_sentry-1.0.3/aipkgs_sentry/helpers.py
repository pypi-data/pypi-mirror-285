import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

try:
    SENTRY_DSN = os.getenv("SENTRY_DSN")
except:
    raise Exception("add SENTRY_DSN to env")


class SentryHelpers:
    @classmethod
    def init_sentry(cls, env: str = None, release: str = None):
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            debug=False,  # if constants.is_in_cloud else True,
            environment=env or '',
            release=release or '',
            # before_send=before_send,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    @classmethod
    def set_user(cls, _id: str, email: str):
        sentry_sdk.set_user({"id": _id,
                             "email": email})

    @classmethod
    def set_user(cls, **kwargs):
        sentry_sdk.set_user(kwargs)

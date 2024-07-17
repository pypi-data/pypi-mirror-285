import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging

# Ensure SENTRY_DSN is set in the environment
try:
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    if not SENTRY_DSN:
        raise ValueError("SENTRY_DSN environment variable is missing.")
except Exception as e:
    logging.error(f"Error loading SENTRY_DSN: {e}")
    raise


class SentryHelpers:
    @classmethod
    def init_sentry(cls, env: str = None, release: str = None, before_send=None):
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            debug=not env == 'production',  # Enable debug mode if not in production
            environment=env or '',
            release=release or '',
            before_send=before_send,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    @classmethod
    def set_user(cls, **kwargs):
        """Set user context for Sentry."""
        sentry_sdk.set_user(kwargs)

    @classmethod
    def clear_user(cls):
        """Clear user context for Sentry."""
        sentry_sdk.set_user(None)

    @classmethod
    def add_breadcrumb(cls, message, level='info', **kwargs):
        """Add a breadcrumb to Sentry."""
        sentry_sdk.add_breadcrumb(message=message, level=level, **kwargs)

    @classmethod
    def capture_exception(cls, exception):
        """Manually capture an exception to Sentry."""
        sentry_sdk.capture_exception(exception)

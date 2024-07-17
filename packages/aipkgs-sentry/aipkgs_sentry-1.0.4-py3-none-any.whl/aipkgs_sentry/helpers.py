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
    def before_send(cls, event, hint):
        """Filter out specific events from being sent to Sentry."""
        # Check if there's an exception in the event and if it's an HTTPException
        exc_info = hint.get('exc_info')
        if exc_info:
            exception_instance = exc_info[1]
            if hasattr(exception_instance, 'code'):
                if exception_instance.code == 401:
                    # Ignore 401 Unauthorized errors
                    return None

        # You can add more custom filtering logic here if needed

        return event

    @classmethod
    def init_sentry(cls, env: str = None, release: str = None):
        """Initialize Sentry with the given environment and release information."""
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            debug=not env == 'production',  # Enable debug mode if not in production
            environment=env or '',
            release=release or '',
            before_send=cls.before_send,  # Add the before_send callback
            traces_sample_rate=1.0,  # Adjust sample rate as needed
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

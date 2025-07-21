import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

def init_sentry():
    sentry_sdk.init(
        dsn="https://479f200bf27f78719ccfb5ce6a93cec6@o4509700386062336.ingest.us.sentry.io/4509700392681472",
        traces_sample_rate=1.0,  # Change to 0.1 for production if needed
    )

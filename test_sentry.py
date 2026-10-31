"""Quick check that Sentry can receive data from this computer."""

import os

import sentry_sdk
from sentry_sdk.consts import VERSION

dsn = os.environ.get("SENTRY_DSN")
print("DSN set:", bool(dsn))
print("Sentry SDK version:", VERSION)

sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0, debug=True)

with sentry_sdk.start_transaction(op="test", name="hello from seance"):
    pass

sentry_sdk.capture_message("seance test message")
sentry_sdk.flush(timeout=10)
print("done")

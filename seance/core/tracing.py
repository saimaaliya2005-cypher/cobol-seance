"""Tracing - optional Sentry agent tracing for the seance.

Turns on only when the SENTRY_DSN environment variable is set and sentry-sdk
is installed. Otherwise every function here quietly does nothing, so the app
works exactly the same without Sentry.

Only metadata is sent (spirit, mode, model, timings, counts). The text of
your messages and the spirit's replies is never sent.
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager

try:
    import sentry_sdk
except ImportError:  # sentry-sdk not installed
    sentry_sdk = None

_enabled = False


def init_tracing() -> bool:
    """Start Sentry if SENTRY_DSN is set. Returns True when tracing is on."""
    global _enabled
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn or sentry_sdk is None:
        return False
    try:
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=1.0,
            send_default_pii=False,
        )
        _enabled = True
    except Exception:
        _enabled = False
    return _enabled


def _set(span, key, value) -> None:
    """Set an attribute on a span, across Sentry SDK versions."""
    if span is None or value is None:
        return
    for method_name in ("set_data", "set_attribute"):
        method = getattr(span, method_name, None)
        if method is None:
            continue
        try:
            method(key, value)
            return
        except Exception:
            continue


@contextmanager
def trace_chat(spirit_name: str, mode: str, model: str):
    """Wrap one spirit reply in an agent-invocation span."""
    cm, span = None, None
    if _enabled:
        try:
            cm = sentry_sdk.start_span(
                op="gen_ai.invoke_agent",
                name=f"invoke_agent {spirit_name}",
            )
            span = cm.__enter__()
            _set(span, "gen_ai.agent.name", spirit_name)
            _set(span, "gen_ai.request.model", model)
            _set(span, "gen_ai.system", "ollama")
            _set(span, "seance.mode", mode)
        except Exception:
            cm, span = None, None

    exc_info = (None, None, None)
    try:
        yield span
    except BaseException:
        exc_info = sys.exc_info()
        raise
    finally:
        if cm is not None:
            try:
                cm.__exit__(*exc_info)
            except Exception:
                pass


async def traced_stream(stream, span):
    """Pass tokens through unchanged while recording model timings on the span.

    time_to_first_token and model_time count only the time spent waiting on
    Ollama, not the typewriter delays, so they reflect real model latency.
    """
    if span is None:
        async for token in stream:
            yield token
        return

    iterator = stream.__aiter__()
    start = time.perf_counter()
    first_token_s = None
    model_time = 0.0
    chunks = 0
    chars = 0

    try:
        while True:
            waited_from = time.perf_counter()
            try:
                token = await iterator.__anext__()
            except StopAsyncIteration:
                break
            model_time += time.perf_counter() - waited_from
            if first_token_s is None:
                first_token_s = time.perf_counter() - start
            chunks += 1
            chars += len(token)
            yield token
    finally:
        _set(span, "seance.time_to_first_token_s", round(first_token_s, 3) if first_token_s else None)
        _set(span, "seance.model_time_s", round(model_time, 3))
        _set(span, "seance.stream_chunks", chunks)
        _set(span, "seance.reply_chars", chars)
        # Ollama streams roughly one token per chunk, so this is approximate.
        _set(span, "gen_ai.usage.output_tokens", chunks)


def capture_error(exc: BaseException) -> None:
    """Report an exception to Sentry (no-op when tracing is off)."""
    if not _enabled:
        return
    try:
        sentry_sdk.capture_exception(exc)
    except Exception:
        pass

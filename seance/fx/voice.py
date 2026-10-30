"""Voice - gives each spirit a voice through the ElevenLabs API.

Everything runs in a background thread, so the seance loop never waits on audio.
Needs: the ELEVENLABS_API_KEY environment variable and `pip install pygame`.
"""

from __future__ import annotations

import io
import os
import re
import sys
import threading

import httpx

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
MODEL_ID = "eleven_multilingual_v2"

# Keep each line short so the free-tier character budget lasts.
MAX_CHARS = 350

# Default premade voices.
ADAM = "pNInz6obpgDQGcFmaJgB"
RACHEL = ADAM
DEFAULT_VOICE = ADAM

# Matched against the spirit's name (lowercase, substring match).
# Swap in different voice IDs to give each spirit its own sound.
VOICES = {
    "cobol": ADAM,
    "fortran": ADAM,
    "algol": ADAM,
    "pascal": ADAM,
    "flash": RACHEL,
    "6502": ADAM,
    "assembly": ADAM,
    "basic": RACHEL,
    "lisp": RACHEL,
}

# Low stability = more unstable, eerie delivery.
VOICE_SETTINGS = {
    "stability": 0.35,
    "similarity_boost": 0.75,
    "style": 0.4,
}

_play_lock = threading.Lock()
_error_shown = False


def voice_for(spirit_name: str) -> str:
    """Pick the voice ID for a spirit."""
    key = spirit_name.lower()
    for keyword, voice_id in VOICES.items():
        if keyword in key:
            return voice_id
    return DEFAULT_VOICE


def clean_for_speech(text: str) -> str:
    """Strip code blocks, *stage directions* and markdown, then trim to MAX_CHARS."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"\*[^*]*\*", " ", text)
    text = re.sub(r"[`_#>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= MAX_CHARS:
        return text

    cut = text[:MAX_CHARS]
    last_end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
    return cut[: last_end + 1] if last_end > 80 else cut


def voice_ready() -> tuple[bool, str]:
    """Check that voice can work. Returns (ok, message to show the user)."""
    if not os.environ.get("ELEVENLABS_API_KEY"):
        return False, "Voice needs the ELEVENLABS_API_KEY environment variable."
    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame  # noqa: F401
    except ImportError:
        return False, "Voice needs pygame. Run: pip install pygame"
    return True, "The spirits can speak now."


def stop_voice() -> None:
    """Cut off any audio that is currently playing."""
    try:
        import pygame

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


def _report_error_once(message: str) -> None:
    global _error_shown
    if not _error_shown:
        _error_shown = True
        print(f"\n  (voice failed: {message})", file=sys.stderr)


def _speak_blocking(text: str, spirit_name: str) -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        return

    text = clean_for_speech(text)
    if not text:
        return

    try:
        response = httpx.post(
            API_URL.format(voice_id=voice_for(spirit_name)),
            headers={"xi-api-key": api_key, "Accept": "audio/mpeg"},
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": VOICE_SETTINGS,
            },
            timeout=30,
        )
        response.raise_for_status()
    except Exception as exc:
        _report_error_once(str(exc))
        return

    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame

        with _play_lock:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(io.BytesIO(response.content), "mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
    except Exception as exc:
        _report_error_once(str(exc))


def speak(text: str, spirit_name: str) -> None:
    """Speak text in the spirit's voice without blocking the caller."""
    threading.Thread(
        target=_speak_blocking, args=(text, spirit_name), daemon=True
    ).start()

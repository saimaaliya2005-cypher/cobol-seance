"""Typewriter effect — reveals text character-by-character with randomized delay."""

from __future__ import annotations

import asyncio
import random
import sys

from rich.console import Console
from rich.text import Text


# Delay ranges in seconds
FAST = (0.005, 0.015)
NORMAL = (0.025, 0.065)
SLOW = (0.04, 0.10)
DRAMATIC = (0.08, 0.18)

# Characters that trigger a longer pause (like natural speech)
PAUSE_CHARS = {".": 0.25, "!": 0.20, "?": 0.22, ",": 0.10, ";": 0.10, ":": 0.08, "\n": 0.15}


async def typewriter_print(
    text: str,
    console: Console,
    speed: tuple[float, float] = NORMAL,
    style: str = "",
    ghost_flicker: bool = True,
) -> None:
    """Print text character-by-character with a typewriter effect.

    Args:
        text: The text to reveal.
        console: Rich console instance for output.
        speed: Tuple of (min_delay, max_delay) in seconds.
        style: Rich style string (e.g., "green", "bold red").
        ghost_flicker: If True, occasionally flicker characters for spooky effect.
    """
    for i, char in enumerate(text):
        # Occasional ghostly flicker — replace char briefly with static
        if ghost_flicker and random.random() < 0.02 and char.strip():
            glitch_char = random.choice("░▒▓█▄▀╳╬")
            console.print(glitch_char, end="", style="dim white")
            await asyncio.sleep(0.05)
            # Backspace to overwrite the glitch with the real character
            sys.stdout.write("\b")
            sys.stdout.flush()

        console.print(char, end="", style=style)

        # Determine delay
        if char in PAUSE_CHARS:
            delay = PAUSE_CHARS[char]
        else:
            delay = random.uniform(*speed)

        await asyncio.sleep(delay)

    # Final newline
    console.print()


async def typewriter_stream(
    token_iterator,
    console: Console,
    speed: tuple[float, float] = FAST,
    style: str = "",
) -> str:
    """Stream tokens from an async iterator with typewriter effect.

    This is designed to work directly with the Ollama streaming response.

    Args:
        token_iterator: Async iterator yielding string tokens.
        console: Rich console instance.
        speed: Delay range per character.
        style: Rich style string.

    Returns:
        The complete accumulated text.
    """
    full_text = ""

    async for token in token_iterator:
        full_text += token
        for char in token:
            # Occasional ghost flicker
            if random.random() < 0.015 and char.strip():
                glitch_char = random.choice("░▒▓█")
                console.print(glitch_char, end="", style="dim white")
                await asyncio.sleep(0.04)
                sys.stdout.write("\b")
                sys.stdout.flush()

            console.print(char, end="", style=style)

            if char in PAUSE_CHARS:
                await asyncio.sleep(PAUSE_CHARS[char] * 0.2)  # Slightly faster for streaming
            else:
                await asyncio.sleep(random.uniform(*speed))

    console.print()  # Final newline
    return full_text

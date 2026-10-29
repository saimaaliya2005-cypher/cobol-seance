"""Glitch effects — random visual corruption for spooky atmosphere."""

from __future__ import annotations

import asyncio
import random

from rich.console import Console


# Glitch character palettes
STATIC_CHARS = "░▒▓█▄▀▐▌╳╬╫╪┼┤├┴┬│─"
CORRUPT_CHARS = "̷̡̢̧̨̛̖̗̘̙̜̝̞̟̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳̹̺̻̼̀́̂̃̄̅̆̇̈̉̊̋̌̍̎̏̐̑̒̓̔̽̾̿̀́͂̓̈́͆͊͋͌̕̚ͅ͏"
GHOST_WORDS = [
    "h̷e̶l̵p̸", "r̵e̶m̷e̶m̵b̷e̶r̵", "f̵o̶r̷g̶o̵t̷t̶e̵n̷",
    "s̸t̵a̶c̷k̸ ̵o̶v̷e̶r̵f̶l̷o̵w̸", "s̵e̶g̷f̵a̶u̵l̷t̸",
    "n̷u̶l̵l̸", "v̵o̶i̷d̸", "̷d̶e̵p̶r̷e̵c̶a̵t̶e̵d̷",
]


async def glitch_burst(
    console: Console,
    intensity: int = 3,
    line_width: int = 60,
) -> None:
    """Display a burst of random static/glitch lines.

    Args:
        console: Rich console instance.
        intensity: Number of glitch lines to show (1-10).
        line_width: Width of each glitch line.
    """
    for _ in range(intensity):
        line = "".join(random.choice(STATIC_CHARS) for _ in range(line_width))
        console.print(line, style="dim white")
        await asyncio.sleep(0.05)

    # Clear the glitch lines by moving cursor up
    for _ in range(intensity):
        console.print(f"\033[A\033[K", end="")
    await asyncio.sleep(0.1)


async def screen_flicker(console: Console, flashes: int = 3) -> None:
    """Simulate a screen flicker effect.

    Args:
        console: Rich console instance.
        flashes: Number of flicker cycles.
    """
    for _ in range(flashes):
        # Brief "blank" moment
        console.print("\033[?5h", end="")  # Reverse video on
        await asyncio.sleep(random.uniform(0.03, 0.08))
        console.print("\033[?5l", end="")  # Reverse video off
        await asyncio.sleep(random.uniform(0.05, 0.15))


async def ghost_interference(
    console: Console,
    duration: float = 1.0,
    width: int = 50,
) -> None:
    """Show sustained ghost interference — static with occasional words.

    Args:
        console: Rich console instance.
        duration: How long the interference lasts (seconds).
        width: Width of static lines.
    """
    end_time = asyncio.get_event_loop().time() + duration
    lines_printed = 0

    while asyncio.get_event_loop().time() < end_time:
        if random.random() < 0.15:
            # Occasionally show a ghostly word in the static
            word = random.choice(GHOST_WORDS)
            padding_left = random.randint(5, width - 15)
            line = (
                "".join(random.choice(STATIC_CHARS) for _ in range(padding_left))
                + f" {word} "
                + "".join(random.choice(STATIC_CHARS) for _ in range(width - padding_left - len(word) - 2))
            )
        else:
            line = "".join(random.choice(STATIC_CHARS) for _ in range(width))

        console.print(line, style="dim green")
        lines_printed += 1
        await asyncio.sleep(0.06)

    # Clean up: erase the interference lines
    for _ in range(lines_printed):
        console.print(f"\033[A\033[K", end="")


def corrupt_text(text: str, corruption_rate: float = 0.1) -> str:
    """Apply random character corruption to text.

    Args:
        text: The text to corrupt.
        corruption_rate: Probability of corrupting each character (0.0 - 1.0).

    Returns:
        The corrupted text string.
    """
    result = []
    for char in text:
        if random.random() < corruption_rate and char.strip():
            # Either replace with static or add combining characters
            if random.random() < 0.5:
                result.append(random.choice(STATIC_CHARS))
            else:
                # Add zalgo-style combining characters
                num_combos = random.randint(1, 3)
                combos = "".join(random.choice(CORRUPT_CHARS) for _ in range(num_combos))
                result.append(char + combos)
        else:
            result.append(char)
    return "".join(result)

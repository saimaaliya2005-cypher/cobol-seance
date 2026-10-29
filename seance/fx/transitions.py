"""Transition animations — summoning, banishing, and switching spirits."""

from __future__ import annotations

import asyncio
import random

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


# Summoning animation frames
PENTAGRAM_FRAMES = [
    """
         ·
        / \\
       /   \\
      ·     ·
       \\   /
        \\ /
         ·
    """,
    """
         ★
        /|\\
       / | \\
      ★--+--★
       \\ | /
        \\|/
         ★
    """,
    """
         ✦
        /█\\
       / █ \\
      ✦══█══✦
       \\ █ /
        \\█/
         ✦
    """,
    """
         ◆
        ╱║╲
       ╱ ║ ╲
      ◆══╬══◆
       ╲ ║ ╱
        ╲║╱
         ◆
    """,
]

CANDLES = [
    "  🕯️  ",
    " 🕯️🕯️ ",
    "🕯️🕯️🕯️",
]


async def summoning_animation(
    spirit_name: str,
    spirit_emoji: str,
    console: Console,
) -> None:
    """Play the spirit summoning animation.

    Args:
        spirit_name: Name of the spirit being summoned.
        spirit_emoji: Emoji for the spirit.
        console: Rich console instance.
    """
    width = 60

    # Phase 1: Candles light up
    console.print()
    for candle_frame in CANDLES:
        centered = candle_frame.center(width)
        console.print(centered, style="yellow")
        await asyncio.sleep(0.4)
    # Clean candle lines
    for _ in range(len(CANDLES)):
        console.print("\033[A\033[K", end="")

    # Phase 2: Pentagram forms
    for frame in PENTAGRAM_FRAMES:
        lines = frame.strip().split("\n")
        for line in lines:
            console.print(line.center(width), style="bold magenta")
        await asyncio.sleep(0.35)
        # Clean frame
        for _ in range(len(lines)):
            console.print("\033[A\033[K", end="")

    # Phase 3: Static burst
    for _ in range(5):
        static = "".join(random.choice("░▒▓█▀▄") for _ in range(width))
        console.print(static, style="dim cyan")
        await asyncio.sleep(0.06)
    for _ in range(5):
        console.print("\033[A\033[K", end="")

    # Phase 4: Spirit name reveal
    console.print()
    reveal_text = f"  ◈ ◈ ◈  {spirit_emoji} {spirit_name} rises from the void  ◈ ◈ ◈  "
    console.print(
        Panel(
            Text(reveal_text, justify="center", style="bold"),
            style="bold green",
            border_style="green",
        )
    )
    console.print()
    await asyncio.sleep(0.5)


async def banishing_animation(
    spirit_name: str,
    console: Console,
) -> None:
    """Play the spirit banishing animation.

    Args:
        spirit_name: Name of the spirit being banished.
        console: Rich console instance.
    """
    width = 50

    console.print()

    # Dissolving effect
    text = f"  {spirit_name} fades back into the void...  "
    for corruption_level in [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        corrupted = ""
        for char in text:
            if random.random() < corruption_level and char.strip():
                corrupted += random.choice("░▒▓ ")
            else:
                corrupted += char
        console.print(corrupted.center(width), style="dim white")
        await asyncio.sleep(0.2)
        console.print("\033[A\033[K", end="")

    # Final message
    console.print(
        "  ...silence returns to the chamber...  ".center(width),
        style="dim italic white",
    )
    console.print()
    await asyncio.sleep(0.3)


async def mode_transition(
    mode_name: str,
    console: Console,
) -> None:
    """Brief visual transition when switching interaction modes.

    Args:
        mode_name: The mode being entered (e.g., 'TRANSLATE', 'TEACH').
        console: Rich console instance.
    """
    divider = "─" * 50
    console.print(divider, style="dim green")
    console.print(f"  ◈ Mode: {mode_name.upper()} ◈  ".center(50), style="bold green")
    console.print(divider, style="dim green")
    await asyncio.sleep(0.3)

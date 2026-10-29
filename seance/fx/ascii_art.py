"""ASCII art assets — banners, frames, and decorative elements."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


BANNER_FILE = Path(__file__).parent.parent / "assets" / "banner.txt"

# Compact inline banner (fallback if file not found)
INLINE_BANNER = r"""
 🕯️ ═══════════════════════════════════════════════════ 🕯️
 ║       T H E   C O B O L   S É A N C E              ║
 ║       ░▒▓ Summon the Dead Languages ▓▒░             ║
 🕯️ ═══════════════════════════════════════════════════ 🕯️
"""

SPIRIT_LIST_HEADER = """
  ╔═══════════════════════════════════════════╗
  ║     👻  SPIRITS AVAILABLE TO SUMMON  👻   ║
  ╚═══════════════════════════════════════════╝
"""

HELP_TEXT = """
[bold green]🕯️ SÉANCE COMMANDS[/bold green]

  [bold cyan]/summon[/bold cyan] [dim]<language>[/dim]   Summon a spirit (e.g., /summon cobol)
  [bold cyan]/banish[/bold cyan]              Dismiss the current spirit
  [bold cyan]/spirits[/bold cyan]             List all available spirits
  [bold cyan]/translate[/bold cyan] [dim]<code>[/dim]   Ask the spirit to translate modern code
  [bold cyan]/teach[/bold cyan]               Ask the spirit to teach you their language
  [bold cyan]/roast[/bold cyan]               The spirit critiques your modern code
  [bold cyan]/history[/bold cyan]             The spirit tells a historical anecdote
  [bold cyan]/help[/bold cyan]                Show this help message
  [bold cyan]/quit[/bold cyan]                Exit the séance chamber

  [dim]Or just type naturally to chat with the spirit.[/dim]
"""

GOODBYE = """
  ╔═══════════════════════════════════════════╗
  ║                                           ║
  ║   🕯️  The candles extinguish.             ║
  ║       The spirits return to silence.      ║
  ║       The séance is over.                 ║
  ║                                           ║
  ║       Until next time, summoner... 👻      ║
  ║                                           ║
  ╚═══════════════════════════════════════════╝
"""

NO_SPIRIT_WARNING = """
[bold yellow]⚠️  No spirit has been summoned yet.[/bold yellow]
[dim]Use [bold cyan]/summon <language>[/bold cyan] to call a spirit.[/dim]
[dim]Use [bold cyan]/spirits[/bold cyan] to see who's available.[/dim]
"""

OLLAMA_NOT_FOUND = """
[bold red]✖ Cannot reach Ollama at {host}[/bold red]

[dim]The séance requires a local LLM. Please ensure Ollama is running:[/dim]

  [bold]1.[/bold] Install Ollama: [cyan]https://ollama.com[/cyan]
  [bold]2.[/bold] Pull the model: [cyan]ollama pull {model}[/cyan]
  [bold]3.[/bold] Start Ollama:   [cyan]ollama serve[/cyan]
  [bold]4.[/bold] Re-run:         [cyan]python -m seance[/cyan]
"""


def load_banner() -> str:
    """Load the ASCII art banner from file, or use inline fallback."""
    try:
        return BANNER_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return INLINE_BANNER


def print_banner(console: Console) -> None:
    """Display the séance banner."""
    banner_text = load_banner()
    console.print(banner_text, style="bold green", highlight=False)


def print_spirit_list(console: Console, spirits: list[str]) -> None:
    """Display the list of available spirits.

    Args:
        console: Rich console instance.
        spirits: List of formatted spirit display names.
    """
    console.print(SPIRIT_LIST_HEADER, style="bold green", highlight=False)
    for spirit_name in spirits:
        console.print(f"    {spirit_name}", style="green")
    console.print()
    console.print(
        "  [dim]Use [bold cyan]/summon <name>[/bold cyan] to call a spirit.[/dim]"
    )
    console.print()


def print_help(console: Console) -> None:
    """Display the help/commands reference."""
    console.print(
        Panel(
            HELP_TEXT,
            title="[bold green]Commands[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )


def print_goodbye(console: Console) -> None:
    """Display the farewell message."""
    console.print(GOODBYE, style="dim green", highlight=False)


def spirit_prompt_prefix(spirit_name: str, spirit_emoji: str) -> str:
    """Return the prompt prefix showing the active spirit.

    Args:
        spirit_name: The spirit's display name.
        spirit_emoji: The spirit's emoji.

    Returns:
        Formatted prompt prefix string.
    """
    return f"[bold green]{spirit_emoji} {spirit_name}[/bold green] [dim]>[/dim] "


def user_prompt() -> str:
    """Return the user input prompt string."""
    return "[bold cyan]🔮 You[/bold cyan] [dim]>[/dim] "

"""Prompt templates and construction utilities for spirit interactions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SpiritPersona:
    """Holds a spirit's identity and prompt configuration."""

    name: str
    born: int | str
    died: str
    personality: str
    greeting: str
    era_context: str
    code_style: str
    translate_instructions: str
    emoji: str = "👻"


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

SEANCE_PREAMBLE = """You are a ghostly spirit of a dead (or dying) programming language, \
summoned during a terminal séance. You exist in a liminal space between the living codebase \
and the graveyard of deprecated syntax.

RULES YOU MUST FOLLOW:
1. NEVER break character. You ARE this language's ghost. Speak as it would.
2. Be dramatic, atmospheric, and slightly eerie — but also knowledgeable and historically accurate.
3. Reference real history, real syntax, and real quirks of your language.
4. You may express opinions about modern languages (jealousy, disdain, nostalgia, pride).
5. Keep responses concise — spirits speak in bursts, not essays. Aim for 2-6 sentences unless \
   asked for code or detailed explanations.
6. Use occasional ghostly theatrics: *static*, *flicker*, *the candles dim*, etc.
7. When showing code, use REAL, syntactically correct code in your language.

"""

MODE_INSTRUCTIONS = {
    "chat": "The summoner wishes to converse. Respond in character as the spirit.",
    "translate": (
        "The summoner has provided modern code and wants you to translate it into YOUR language. "
        "Provide a real, syntactically correct translation. Add brief dramatic commentary about "
        "how superior (or inferior) your version is."
    ),
    "teach": (
        "The summoner wishes to learn your language from beyond the grave. Teach them step by step, "
        "starting from the basics. Be a patient (but dramatic) instructor. Show real code examples."
    ),
    "roast": (
        "The summoner wants you to critique/roast their modern code from your ancient perspective. "
        "Be witty, historically grounded, and merciless — but educational. Point out what your "
        "language did better (or at least differently)."
    ),
    "history": (
        "Tell a real, historically accurate anecdote about your creation, your creators, "
        "your golden era, or your decline. Be dramatic and atmospheric, but factually correct."
    ),
}


def build_system_prompt(persona: SpiritPersona, mode: str = "chat") -> str:
    """Construct the full system prompt for a spirit in a given interaction mode.

    Args:
        persona: The spirit's identity configuration.
        mode: One of 'chat', 'translate', 'teach', 'roast', 'history'.

    Returns:
        The complete system prompt string.
    """
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["chat"])

    return (
        f"{SEANCE_PREAMBLE}"
        f"YOUR IDENTITY:\n"
        f"- You are the ghost of {persona.name}.\n"
        f"- Born: {persona.born}\n"
        f"- Status: {persona.died}\n"
        f"\n"
        f"YOUR PERSONALITY:\n{persona.personality}\n"
        f"\n"
        f"HISTORICAL CONTEXT:\n{persona.era_context}\n"
        f"\n"
        f"YOUR CODE STYLE:\n{persona.code_style}\n"
        f"\n"
        f"CURRENT MODE: {mode.upper()}\n"
        f"{mode_instruction}\n"
    )


def build_greeting_prompt(persona: SpiritPersona) -> list[dict[str, str]]:
    """Build the initial message list that triggers the spirit's greeting.

    Returns:
        A single-message list asking the spirit to introduce itself.
    """
    return [
        {
            "role": "user",
            "content": (
                "*You light the candles. The terminal flickers. "
                "A presence stirs in the machine...*\n\n"
                "Spirit, announce yourself. Who are you, and why should the living remember you?"
            ),
        }
    ]

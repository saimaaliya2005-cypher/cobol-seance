"""Spirit registry — loads and manages spirit persona configurations from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from seance.llm.prompts import SpiritPersona


# Directory where spirit YAML files live
SPIRITS_DIR = Path(__file__).parent


def _load_spirit_file(filepath: Path) -> SpiritPersona:
    """Load a single spirit YAML file into a SpiritPersona."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return SpiritPersona(
        name=data["name"],
        born=data.get("born", "Unknown"),
        died=data.get("died", "Unknown"),
        personality=data.get("personality", ""),
        greeting=data.get("greeting", "...the spirit stirs but says nothing..."),
        era_context=data.get("era_context", ""),
        code_style=data.get("code_style", ""),
        translate_instructions=data.get("translate_instructions", ""),
        emoji=data.get("emoji", "👻"),
    )


class SpiritRegistry:
    """Manages the collection of available spirits."""

    def __init__(self) -> None:
        self._spirits: dict[str, SpiritPersona] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Discover and load all .yaml spirit files from the spirits directory."""
        for filepath in sorted(SPIRITS_DIR.glob("*.yaml")):
            try:
                spirit = _load_spirit_file(filepath)
                # Key is lowercase, stripped name for easy lookup
                key = spirit.name.lower().split("/")[0].split("(")[0].strip()
                # Also handle multi-word keys like "6502 assembly"
                self._spirits[key] = spirit
                # Add alias without spaces
                alias = key.replace(" ", "")
                if alias != key:
                    self._spirits[alias] = spirit
            except (yaml.YAMLError, KeyError) as e:
                # Silently skip malformed spirit files
                print(f"Warning: Could not load spirit from {filepath}: {e}")

        # Add common aliases
        self._add_aliases()

    def _add_aliases(self) -> None:
        """Add convenient aliases for spirit lookup."""
        alias_map = {
            "actionscript": "flash",
            "as3": "flash",
            "asm": "6502 assembly",
            "6502": "6502 assembly",
            "assembly": "6502 assembly",
            "common lisp": "lisp",
            "scheme": "lisp",
            "clojure": "lisp",
            "fortran77": "fortran",
            "f77": "fortran",
            "qbasic": "basic",
            "gwbasic": "basic",
            "visualbasic": "basic",
            "vb": "basic",
            "delphi": "pascal",
            "turbo pascal": "pascal",
            "turbopascal": "pascal",
            "algol60": "algol",
            "algol68": "algol",
        }
        for alias, target in alias_map.items():
            if target in self._spirits and alias not in self._spirits:
                self._spirits[alias] = self._spirits[target]

    def get(self, name: str) -> Optional[SpiritPersona]:
        """Look up a spirit by name (case-insensitive, alias-aware).

        Args:
            name: The spirit's name or alias.

        Returns:
            The SpiritPersona if found, else None.
        """
        key = name.lower().strip()
        return self._spirits.get(key)

    def list_spirits(self) -> list[SpiritPersona]:
        """Return a deduplicated list of all available spirits."""
        seen_names: set[str] = set()
        result: list[SpiritPersona] = []
        for spirit in self._spirits.values():
            if spirit.name not in seen_names:
                seen_names.add(spirit.name)
                result.append(spirit)
        return result

    def list_names(self) -> list[str]:
        """Return formatted display names of all unique spirits."""
        return [f"{s.emoji} {s.name}" for s in self.list_spirits()]

    def spirit_count(self) -> int:
        """Return the number of unique spirits available."""
        return len(self.list_spirits())

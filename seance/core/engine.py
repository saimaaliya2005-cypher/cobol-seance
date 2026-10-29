"""Séance Engine — the core orchestrator that runs the interactive séance loop."""

from __future__ import annotations

import asyncio
import sys

from rich.console import Console
from rich.prompt import Prompt

from seance.core.conversation import Conversation
from seance.fx.ascii_art import (
    OLLAMA_NOT_FOUND,
    NO_SPIRIT_WARNING,
    print_banner,
    print_goodbye,
    print_help,
    print_spirit_list,
)
from seance.fx.glitch import ghost_interference, glitch_burst
from seance.fx.transitions import (
    banishing_animation,
    mode_transition,
    summoning_animation,
)
from seance.fx.typewriter import typewriter_print, typewriter_stream, SLOW, DRAMATIC
from seance.llm.ollama_client import OllamaClient
from seance.llm.prompts import (
    SpiritPersona,
    build_greeting_prompt,
    build_system_prompt,
)
from seance.spirits.registry import SpiritRegistry

Prompt.prompt_suffix = ""


class SeanceEngine:
    """Main engine that orchestrates the séance experience."""

    def __init__(
        self,
        model: str = "gemma3:4b",
        ollama_host: str = "http://localhost:11434",
        voice: bool = False,
    ):
        self.model = model
        self.ollama_host = ollama_host
        self.voice = voice

        self.console = Console()
        self.llm = OllamaClient(host=ollama_host, model=model)
        self.registry = SpiritRegistry()
        self.conversation = Conversation()

        self._current_spirit: SpiritPersona | None = None
        self._current_mode: str = "chat"
        self._running: bool = False

    def run(self) -> None:
        """Start the séance (sync wrapper around the async loop)."""
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            self.console.print()
            print_goodbye(self.console)

    async def _run_async(self) -> None:
        """Main async event loop."""
        # Show banner
        print_banner(self.console)

        # Check Ollama connection
        self.console.print("  [dim]Reaching into the void...[/dim]", end="")
        connected = await self.llm.check_connection()
        if not connected:
            self.console.print()
            self.console.print(
                OLLAMA_NOT_FOUND.format(host=self.ollama_host, model=self.model)
            )
            await self.llm.close()
            return

        self.console.print(" [green]connected.[/green]")

        # Check model availability
        self.console.print(f"  [dim]Channeling model: {self.model}...[/dim]", end="")
        model_ready = await self.llm.check_model_available()
        if not model_ready:
            self.console.print(f" [yellow]not found.[/yellow]")
            models = await self.llm.list_models()
            if models:
                self.console.print(f"  [dim]Available models: {', '.join(models)}[/dim]")
            self.console.print(
                f"  [dim]Pull it with: [cyan]ollama pull {self.model}[/cyan][/dim]"
            )
            await self.llm.close()
            return

        self.console.print(" [green]ready.[/green]")
        self.console.print()

        # Show initial help
        self.console.print(
            "  [dim]Type [bold cyan]/help[/bold cyan] for commands, "
            "or [bold cyan]/summon <language>[/bold cyan] to begin.[/dim]"
        )
        self.console.print()

        # Main loop
        self._running = True
        try:
            while self._running:
                await self._process_input()
        finally:
            await self.llm.close()

    async def _process_input(self) -> None:
        """Read and process one user input."""
        try:
            # Build prompt based on whether a spirit is active
            if self._current_spirit:
                prompt_text = (
                    f"[bold cyan]🔮 You[/bold cyan] "
                    f"[dim](→ {self._current_spirit.emoji} {self._current_spirit.name})[/dim]"
                    f" [dim]>[/dim] "
                )
            else:
                prompt_text = "[bold cyan]🔮 You[/bold cyan] [dim]>[/dim] "

            user_input = Prompt.ask(prompt_text, console=self.console)
            user_input = user_input.strip()

            if not user_input:
                return

        except (EOFError, KeyboardInterrupt):
            self._running = False
            self.console.print()
            print_goodbye(self.console)
            return

        # Route commands vs free chat
        if user_input.startswith("/"):
            await self._handle_command(user_input)
        else:
            await self._handle_chat(user_input)

    async def _handle_command(self, raw_input: str) -> None:
        """Parse and execute a slash command."""
        parts = raw_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "/quit" or command == "/exit":
            self._running = False
            print_goodbye(self.console)

        elif command == "/help":
            print_help(self.console)

        elif command == "/spirits":
            print_spirit_list(self.console, self.registry.list_names())

        elif command == "/summon":
            await self._summon_spirit(arg)

        elif command == "/banish":
            await self._banish_spirit()

        elif command == "/translate":
            if not self._current_spirit:
                self.console.print(NO_SPIRIT_WARNING)
                return
            await mode_transition("translate", self.console)
            self._current_mode = "translate"
            if arg:
                await self._handle_chat(arg)

        elif command == "/teach":
            if not self._current_spirit:
                self.console.print(NO_SPIRIT_WARNING)
                return
            await mode_transition("teach", self.console)
            self._current_mode = "teach"
            await self._handle_chat(
                "Teach me the basics of your language. Start from the very beginning."
            )

        elif command == "/roast":
            if not self._current_spirit:
                self.console.print(NO_SPIRIT_WARNING)
                return
            await mode_transition("roast", self.console)
            self._current_mode = "roast"
            if arg:
                await self._handle_chat(arg)
            else:
                self.console.print(
                    "  [dim]Paste the code you want roasted, or type it after this command.[/dim]"
                )

        elif command == "/history":
            if not self._current_spirit:
                self.console.print(NO_SPIRIT_WARNING)
                return
            await mode_transition("history", self.console)
            self._current_mode = "history"
            await self._handle_chat(
                "Tell me a fascinating true story from your history — something most people don't know."
            )

        elif command == "/mode":
            if not self._current_spirit:
                self.console.print(NO_SPIRIT_WARNING)
                return
            if arg and arg.lower() in ("chat", "translate", "teach", "roast", "history"):
                self._current_mode = arg.lower()
                await mode_transition(self._current_mode, self.console)
            else:
                self.console.print(
                    f"  [dim]Current mode: [bold]{self._current_mode}[/bold]. "
                    f"Options: chat, translate, teach, roast, history[/dim]"
                )

        else:
            self.console.print(
                f"  [dim]Unknown command: {command}. Type [bold cyan]/help[/bold cyan] for options.[/dim]"
            )

    async def _summon_spirit(self, name: str) -> None:
        """Summon a spirit by name."""
        if not name:
            self.console.print(
                "  [dim]Usage: [bold cyan]/summon <language>[/bold cyan] "
                "(e.g., /summon cobol)[/dim]"
            )
            print_spirit_list(self.console, self.registry.list_names())
            return

        spirit = self.registry.get(name)
        if not spirit:
            self.console.print(
                f"  [yellow]No spirit named '{name}' found in the graveyard.[/yellow]"
            )
            self.console.print(
                "  [dim]Use [bold cyan]/spirits[/bold cyan] to see available spirits.[/dim]"
            )
            return

        # Banish current spirit if one is active
        if self._current_spirit:
            await self._banish_spirit(silent=True)

        self._current_spirit = spirit
        self._current_mode = "chat"
        self.conversation.clear()

        # Play summoning animation
        await summoning_animation(spirit.name, spirit.emoji, self.console)

        # Brief interference
        await ghost_interference(self.console, duration=0.6, width=50)

        # Generate and display the spirit's greeting
        system_prompt = build_system_prompt(spirit, mode="chat")
        greeting_messages = build_greeting_prompt(spirit)

        self.console.print(
            f"  {spirit.emoji} [bold green]{spirit.name}[/bold green] [dim]>[/dim] ",
            end="",
        )

        # Stream the greeting with typewriter effect
        full_response = await typewriter_stream(
            self.llm.stream_chat(system_prompt, greeting_messages),
            self.console,
            style="green",
        )

        # Store the greeting exchange in conversation history
        self.conversation.add_user_message(greeting_messages[0]["content"])
        self.conversation.add_assistant_message(full_response)

        self.console.print()

    async def _banish_spirit(self, silent: bool = False) -> None:
        """Banish the current spirit."""
        if not self._current_spirit:
            if not silent:
                self.console.print(
                    "  [dim]There is no spirit to banish. The chamber is empty.[/dim]"
                )
            return

        spirit_name = self._current_spirit.name

        if not silent:
            await glitch_burst(self.console, intensity=3)
            await banishing_animation(spirit_name, self.console)

        self._current_spirit = None
        self._current_mode = "chat"
        self.conversation.clear()

    async def _handle_chat(self, user_input: str) -> None:
        """Send a message to the current spirit and display the response."""
        if not self._current_spirit:
            self.console.print(NO_SPIRIT_WARNING)
            return

        spirit = self._current_spirit

        # Add context based on current mode
        if self._current_mode == "translate" and not user_input.lower().startswith("translate"):
            user_input = f"Translate this code to {spirit.name}:\n\n{user_input}"
        elif self._current_mode == "roast" and not user_input.lower().startswith("roast"):
            user_input = f"Roast/critique this code from your perspective:\n\n{user_input}"

        # Build the prompt
        self.conversation.add_user_message(user_input)
        system_prompt = build_system_prompt(spirit, mode=self._current_mode)
        messages = self.conversation.to_messages_list()

        # Brief glitch before response
        await glitch_burst(self.console, intensity=1)

        # Display spirit prefix
        self.console.print(
            f"  {spirit.emoji} [bold green]{spirit.name}[/bold green] [dim]>[/dim] ",
            end="",
        )

        # Stream response with typewriter effect
        try:
            full_response = await typewriter_stream(
                self.llm.stream_chat(system_prompt, messages),
                self.console,
                style="green",
            )

            # Store response in history
            self.conversation.add_assistant_message(full_response)

        except Exception as e:
            self.console.print(
                f"\n  [red]✖ The spirit's voice falters: {e}[/red]"
            )

        # Reset mode to chat after one-shot modes
        if self._current_mode in ("history",):
            self._current_mode = "chat"

        self.console.print()

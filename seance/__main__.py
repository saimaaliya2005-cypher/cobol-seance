"""Entry point for the Cobol Séance application."""

import click

from seance.core.engine import SeanceEngine


@click.command()
@click.option(
    "--model",
    default="gemma3:4b",
    help="Ollama model to use for spirit channeling.",
)
@click.option(
    "--ollama-host",
    default="http://localhost:11434",
    help="Ollama server URL.",
)
@click.option(
    "--voice",
    is_flag=True,
    default=False,
    help="Enable ElevenLabs voice output (requires 'voice' extras).",
)
def main(model: str, ollama_host: str, voice: bool) -> None:
    """🕯️ The Cobol Séance — Summon the spirits of dead programming languages."""
    engine = SeanceEngine(model=model, ollama_host=ollama_host, voice=voice)
    engine.run()


if __name__ == "__main__":
    main()

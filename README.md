# 🕯️ The COBOL Séance

**Summon the ghosts of dead (or "dead") programming languages and talk to them.**

A terminal app where eight legacy languages come back as spirits with their own personalities, grudges and ways of speaking. It runs **100% locally** with [Ollama](https://ollama.com) and **Gemma 3 (4B)**. No cloud, no API keys, no internet needed once the model is downloaded.

> **YOU:** are you dead?
>
> **COBOL:** I AM COBOL. I PROCESS TRILLIONS OF DOLLARS DAILY. IT IS NOT "DEAD," UNDERSTAND? IT IS... ACTIVE. I AM HERE.

<!-- Replace with your demo GIF or screenshot -->
![Demo](demo.gif)

## The Spirits

| Spirit | Personality |
|---|---|
| 🏛️ COBOL | Proud bureaucrat. SPEAKS IN UPPERCASE. Offended that you think it's dead. |
| ⚡ Fortran | Grizzled scientist who invented the compiler. Has opinions about NumPy. |
| 🎩 ALGOL | Aristocratic ancestor of everything. Wears a monocle. |
| 🎓 Pascal | Strict teacher with a ruler. Disappointed in JavaScript. |
| 🎮 Flash | Bitter millennial. Misses Newgrounds. |
| 🧮 6502 Assembly | Minimalist monk. Thinks in hex. Judges your RAM usage. |
| 📞 BASIC | The friendliest ghost ever. Loves beginners and line numbers. |
| 🌊 Lisp | Zen philosopher. Parentheses are enlightenment. |

## Commands

| Command | What it does |
|---|---|
| `/summon <language>` | Summon a spirit (e.g. `/summon cobol`) |
| `/banish` | Send the current spirit away |
| `/spirits` | List all available spirits |
| `/translate <code>` | Spirit rewrites your code in its own language |
| `/teach` | Learn the basics from the spirit, in character |
| `/roast <code>` | Get your code critiqued by someone who was there first |
| `/history` | Hear a real story from the language's past |
| `/mode <name>` | Switch mode: `chat`, `translate`, `teach`, `roast`, `history` |
| `/voice on` / `/voice off` | Toggle spoken replies (ElevenLabs) |
| `/help` | Show all commands |
| `/quit` | Leave the séance |

Anything that doesn't start with `/` is just chat with the current spirit.

## Quick Start

**1. Install Ollama and pull the model**

Download Ollama from [ollama.com](https://ollama.com), then:

```bash
ollama pull gemma3:4b
```

**2. Clone and install**

```bash
git clone https://github.com/YOUR-USERNAME/cobol-seance.git
cd cobol-seance
pip install -e .
```

Or install the dependencies directly:

```bash
pip install textual rich httpx pyyaml click pygame
```

**3. Run it**

Make sure Ollama is running (the tray app, or `ollama serve`), then from the project folder:

```bash
python -m seance
```

Type `/summon cobol` to begin.

## 🎙️ Voice (Optional)

Each spirit can speak its replies aloud through the [ElevenLabs](https://elevenlabs.io) text-to-speech API, with a different voice per spirit: a stern voice for COBOL, a cheerful one for BASIC, and so on.

Voice is **opt-in** and everything else still runs locally.

1. Create an ElevenLabs account and an API key with **Text to Speech** access.
2. Install the audio player:
   ```bash
   pip install pygame
   ```
3. Set your key, then run the app (Windows CMD shown):
   ```bash
   set ELEVENLABS_API_KEY=your_key_here
   python -m seance
   ```
4. Inside the séance, type `/voice on`.

Voices are configured in `seance/fx/voice.py`. Replace the voice IDs in the `VOICES` dictionary to give any spirit a new sound. Replies are trimmed to a short length and code blocks are skipped, so the free tier lasts longer. Audio plays in a background thread, so it never blocks the typewriter effect.

## How It Works

- **Persona system:** each spirit is a YAML file with personality, greeting, era context, code style and translation rules. Adding a new spirit means adding one YAML file, no code changes.
- **Registry:** auto-discovers spirit files and supports aliases (e.g. `asm` finds 6502 Assembly).
- **Prompt layering:** a shared séance preamble sets the rules, then a per-mode block changes behavior for chat, translate, teach, roast or history.
- **Streaming:** an async `httpx` client streams tokens from Ollama, and a typewriter layer reveals them character by character with natural pauses and occasional ghostly flickers.
- **Effects:** glitch bursts, ghost interference and a four-phase summoning animation, built with Rich.
- **Conversation memory:** a rolling window of recent messages that always keeps the opening greeting, so the spirit stays in character without overflowing a small model's context.

## Project Structure

```
cobol-seance/
├── pyproject.toml
└── seance/
    ├── __main__.py        # CLI entry point
    ├── core/              # Engine and conversation manager
    ├── llm/               # Ollama client and prompt builders
    ├── spirits/           # Spirit YAML files and registry
    ├── fx/                # Typewriter, glitch, transitions, ASCII art
    └── assets/            # Banner
```

## Known Limitations

This runs on a 4B-parameter model, so it has real limits:

- **Style drift:** a spirit can slip out of character rules (like COBOL's all-caps) in longer replies.
- **Translated code is flavor, not a compiler.** The output looks like the target language but may not compile or run. Don't ship it to production.
- **First response is slow** while Ollama loads the model into memory.
- **Cosmetic bug:** some terminals show stray escape codes (`[A[K`) before a spirit's name after the glitch effect.

A larger Gemma variant should hold character and translate code better. Change it with the model setting in the engine.

## Add Your Own Spirit

1. Copy any file in `seance/spirits/` (for example `cobol.yaml`).
2. Change the name, personality, greeting, code style and translation rules.
3. Run the app and use `/summon <your-spirit>`.

Perl, Visual Basic, Delphi and Smalltalk are all waiting.

## Built With

Python, [Ollama](https://ollama.com), Gemma 3 (4B), Rich, Click, httpx, PyYAML.

Built for the Hacktoberfest Open-Source AI Challenge: *Ghost in the Machine*.

## License

MIT

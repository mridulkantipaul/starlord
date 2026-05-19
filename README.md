# Star Lord

A JARVIS-like **personal AI agent** built for **local-first** use on desktop and mobile. Star Lord is designed to support **voice-first** interaction (with text fallback), act as a **coding helper**, and integrate with **smart home** control—while staying **open-source** and privacy-friendly.

> Status: initial scaffold + **voice adapters (STT/TTS)** + **mobile scaffolding** + **desktop GUI**

## Goals
- Personal assistant (tasks, reminders, knowledge, workflows)
- Coding helper (project guidance, quick fixes, explanations)
- Smart home control (IoT and device orchestration)
- Local-first & open-source friendly

## Quick Start (Text-Only Stub)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m starlord.app
```

## Desktop GUI
```bash
python -m starlord.app --gui
```

## Voice (Open-Source)
See `VOICE.md` for supported engines and setup notes.

## Mobile
See `MOBILE.md` for Android/iOS scaffolding and next steps.

## Structure
- `src/starlord/app.py` — CLI entrypoint
- `src/starlord/gui.py` — desktop GUI (Tkinter)
- `src/starlord/core/` — agent core (router, memory, orchestrator)
- `src/starlord/io/` — input/output adapters (speech + text)
- `src/starlord/tools/` — integrations (GitHub, system, files, browser, IoT)
- `src/starlord/skills/` — skill modules
- `src/starlord/plugins/` — plugin interface

## Docs
- `ARCHITECTURE.md` — core architecture & flow
- `ROADMAP.md` — near-term milestones
- `CONTRIBUTING.md` — contribution guidelines
- `VOICE.md` — STT/TTS adapters and setup
- `MOBILE.md` — mobile scaffolding

## License
TBD (open-source)

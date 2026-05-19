<img width="1536" height="1024" alt="StarLord" src="https://github.com/user-attachments/assets/4d6a8559-38aa-47c6-8259-13697cd9972f" />
# Star Lord

A JARVIS-like **personal AI agent** built for **local-first** use on desktop and mobile. Star Lord is designed to support **voice-first** interaction (with text fallback), act as a **coding helper**, and integrate with **smart home** control—while staying **open-source** and privacy-friendly.

> Status: full desktop experience (Windows-first) + voice + mobile scaffolding

## Quick Start (CLI)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m starlord.app
```

## Desktop GUI (Professional Qt)
```bash
python -m starlord.app --gui-qt
```

## Desktop GUI (Lightweight Tk)
```bash
python -m starlord.app --gui
```

## Features
- Chat history + sessions (UI stub)
- Voice input/output controls (TTS wired, STT adapters ready)
- File explorer + file tools
- Code assistant panel (stub)
- Task/Reminder system
- Tool plugins manager
- Settings panel (models, voice, paths)
- Background agent (system tray)
- Local API server (`/health`, `/chat`)
- Memory layer (file + simple vector)

## Docs
- `VOICE.md`
- `MOBILE.md`

## License
TBD (open-source)

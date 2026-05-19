<img width="1536" height="1024" alt="db302157-b800-484d-b15d-a282e9e612ba" src="https://github.com/user-attachments/assets/7c3282c9-5b10-4f5a-97b1-fa3dfc1409b9" />
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

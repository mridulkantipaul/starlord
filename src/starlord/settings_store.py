"""Settings persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from starlord.config.settings import Settings


SETTINGS_PATH = Path.home() / ".starlord" / "settings.json"


def load_settings() -> Settings:
    if not SETTINGS_PATH.exists():
        return Settings()
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        return Settings(**data)
    except Exception:
        return Settings()


def save_settings(settings: Settings) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = asdict(settings)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

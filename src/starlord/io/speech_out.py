"""Text-to-speech adapters (open-source).

Supported (by adapter):
- Piper (offline, via CLI)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional

from starlord.config.settings import Settings


class SpeechSynthesizer:
    """Base TTS interface."""

    def speak(self, text: str) -> str:
        """Synthesize speech and return output file path."""
        raise NotImplementedError


@dataclass
class PiperSpeechSynthesizer(SpeechSynthesizer):
    model_path: Optional[str] = None
    output_path: str = "./starlord_tts.wav"

    def speak(self, text: str) -> str:
        if not self.model_path:
            raise RuntimeError("Piper model_path is required for TTS.")
        cmd = ["piper", "--model", self.model_path, "--output_file", self.output_path]
        subprocess.run(cmd, input=text, text=True, check=True)
        return self.output_path


def create_speech_synthesizer(settings: Settings) -> SpeechSynthesizer:
    engine = settings.tts_engine.lower()
    if engine == "piper":
        return PiperSpeechSynthesizer(
            model_path=settings.tts_model_path,
            output_path=settings.tts_output_path,
        )
    raise ValueError(f"Unsupported TTS engine: {settings.tts_engine}")

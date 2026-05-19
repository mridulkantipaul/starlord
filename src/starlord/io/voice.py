"""Voice IO convenience wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from starlord.config.settings import Settings
from starlord.io.speech_in import create_speech_recognizer
from starlord.io.speech_out import create_speech_synthesizer


@dataclass
class VoiceIO:
    settings: Settings

    def listen(self) -> str:
        recognizer = create_speech_recognizer(self.settings)
        return recognizer.listen()

    def speak(self, text: str) -> str:
        synthesizer = create_speech_synthesizer(self.settings)
        return synthesizer.speak(text)

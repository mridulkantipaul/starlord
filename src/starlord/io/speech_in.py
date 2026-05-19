"""Speech-to-text adapters (open-source).

Supported (by adapter):
- Vosk (offline)
- Whisper (offline, heavier)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from starlord.config.settings import Settings


class SpeechRecognizer:
    """Base STT interface."""

    def listen(self) -> str:
        """Listen from microphone (optional)."""
        raise NotImplementedError

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an audio file."""
        raise NotImplementedError


@dataclass
class VoskSpeechRecognizer(SpeechRecognizer):
    model_path: Optional[str] = None

    def _load_model(self):
        try:
            from vosk import Model
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Vosk not installed. Install 'vosk' to use this adapter.") from exc
        return Model(self.model_path) if self.model_path else Model(lang="en-us")

    def transcribe_file(self, audio_path: str) -> str:
        import json
        import wave

        model = self._load_model()
        try:
            from vosk import KaldiRecognizer
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Vosk not installed. Install 'vosk' to use this adapter.") from exc

        with wave.open(audio_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
            result = json.loads(rec.FinalResult())
            return result.get("text", "")

    def listen(self) -> str:
        try:
            import sounddevice as sd
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("sounddevice not installed; microphone input unavailable.") from exc

        model = self._load_model()
        try:
            from vosk import KaldiRecognizer
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Vosk not installed. Install 'vosk' to use this adapter.") from exc

        samplerate = 16000
        rec = KaldiRecognizer(model, samplerate)

        def callback(indata, frames, time, status):
            if status:
                pass
            rec.AcceptWaveform(bytes(indata))

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16", channels=1, callback=callback):
            return rec.FinalResult()


@dataclass
class WhisperSpeechRecognizer(SpeechRecognizer):
    model_name: str = "base"

    def _load_model(self):
        try:
            import whisper
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("openai-whisper not installed. Install 'openai-whisper' to use this adapter.") from exc
        return whisper.load_model(self.model_name)

    def transcribe_file(self, audio_path: str) -> str:
        model = self._load_model()
        result = model.transcribe(audio_path)
        return result.get("text", "")


def create_speech_recognizer(settings: Settings) -> SpeechRecognizer:
    engine = settings.stt_engine.lower()
    if engine == "vosk":
        return VoskSpeechRecognizer(model_path=settings.stt_model_path)
    if engine == "whisper":
        return WhisperSpeechRecognizer()
    raise ValueError(f"Unsupported STT engine: {settings.stt_engine}")

"""Configuration settings for Star Lord."""

from dataclasses import dataclass


@dataclass
class Settings:
    agent_name: str = "Star Lord"
    voice_enabled: bool = False
    offline_first: bool = True

    # Speech-to-Text (STT)
    stt_engine: str = "vosk"  # options: vosk, whisper
    stt_model_path: str | None = None

    # Text-to-Speech (TTS)
    tts_engine: str = "piper"  # options: piper
    tts_model_path: str | None = None
    tts_output_path: str = "./starlord_tts.wav"


DEFAULT_SETTINGS = Settings()

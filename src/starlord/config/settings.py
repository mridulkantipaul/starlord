"""Configuration settings for Star Lord."""

from dataclasses import dataclass


@dataclass
class Settings:
    agent_name: str = "Star Lord"
    voice_enabled: bool = False
    offline_first: bool = True


DEFAULT_SETTINGS = Settings()

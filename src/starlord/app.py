"""CLI entrypoint for Star Lord."""

from __future__ import annotations

import argparse

from starlord.config.settings import Settings
from starlord.core.agent import Agent
from starlord.io.text_io import read_text, write_text
from starlord.io.voice import VoiceIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Star Lord CLI")
    parser.add_argument("--voice", action="store_true", help="Enable voice output (TTS)")
    parser.add_argument("--gui", action="store_true", help="Launch desktop GUI")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.gui:
        from starlord.gui import main as gui_main

        gui_main()
        return

    settings = Settings(voice_enabled=bool(args.voice))
    agent = Agent(name=settings.agent_name)
    voice = VoiceIO(settings)

    write_text("Star Lord online (text-only stub). Type 'exit' to quit.")
    while True:
        user_text = read_text().strip()
        if user_text.lower() in {"exit", "quit"}:
            break
        response = agent.handle_input(user_text)
        write_text(response)
        if settings.voice_enabled:
            try:
                output_path = voice.speak(response)
                write_text(f"TTS output: {output_path}")
            except Exception as exc:
                write_text(f"TTS error: {exc}")


if __name__ == "__main__":
    main()

"""CLI entrypoint for Star Lord."""

from starlord.core.agent import Agent
from starlord.io.text_io import read_text, write_text


def main() -> None:
    agent = Agent()
    write_text("Star Lord online (text-only stub). Type 'exit' to quit.")
    while True:
        user_text = read_text().strip()
        if user_text.lower() in {"exit", "quit"}:
            break
        response = agent.handle_input(user_text)
        write_text(response)


if __name__ == "__main__":
    main()

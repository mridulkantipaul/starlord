"""Text input/output adapter (CLI stub)."""


def read_text() -> str:
    return input("> ")


def write_text(text: str) -> None:
    print(text)

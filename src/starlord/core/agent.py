"""Core agent orchestrator."""

from starlord.core.router import IntentRouter


class Agent:
    def __init__(self, name: str = "Star Lord") -> None:
        self.name = name
        self.router = IntentRouter()

    def handle_input(self, user_text: str) -> str:
        """Route input and return a response string (stub)."""
        intent = self.router.route(user_text)
        return f"[{self.name}] Intent={intent} | Response: (stub)"

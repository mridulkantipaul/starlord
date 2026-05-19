"""Intent router (stub)."""


class IntentRouter:
    def route(self, text: str) -> str:
        text_lower = text.lower()
        if "code" in text_lower or "bug" in text_lower:
            return "coding_helper"
        if "light" in text_lower or "home" in text_lower:
            return "smart_home"
        return "personal_assistant"

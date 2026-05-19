"""Modular command system for text, voice, and file inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from starlord.config.settings import Settings
from starlord.core.agent import Agent
from starlord.io.voice import VoiceIO
from starlord.memory_store import FileMemoryStore, MemoryItem, SimpleVectorMemory

FILE_CONTENT_PREVIEW_CHARS = 1200


class CommandError(RuntimeError):
    """Base command error for user-facing command failures."""


class MissingDependencyError(CommandError):
    """Raised when optional runtime dependencies are missing."""


class UserInputError(CommandError):
    """Raised for user-fixable input problems."""


@dataclass
class SessionState:
    name: str
    history: List[str] = field(default_factory=list)
    last_response: str = ""


class AgentCommandSystem:
    def __init__(
        self,
        agent: Agent,
        settings: Settings,
        memory_file: FileMemoryStore,
        vector_memory: SimpleVectorMemory,
    ) -> None:
        self.agent = agent
        self.voice = VoiceIO(settings)
        self.memory_file = memory_file
        self.vector_memory = vector_memory
        self.sessions: Dict[str, SessionState] = {"Default": SessionState(name="Default")}
        self.active_session = "Default"
        self._stop_requested = False

    def create_session(self, name: str) -> SessionState:
        session_name = name.strip() or f"Session {len(self.sessions) + 1}"
        session = SessionState(name=session_name)
        self.sessions[session_name] = session
        self.active_session = session_name
        return session

    def switch_session(self, name: str) -> SessionState:
        self.active_session = name if name in self.sessions else "Default"
        return self.sessions[self.active_session]

    def current_session(self) -> SessionState:
        return self.sessions[self.active_session]

    def request_stop(self) -> str:
        self._stop_requested = True
        return "Stop requested."

    def handle_text(self, text: str) -> str:
        self._stop_requested = False
        session = self.current_session()
        session.history.append(f"> {text}")
        response = self.agent.handle_input(text)
        if self._stop_requested:
            response = "Action stopped."
        session.last_response = response
        session.history.append(response)
        item = MemoryItem(text=text)
        self.memory_file.add(item)
        self.vector_memory.add(item)
        return response

    def handle_voice(self) -> str:
        self._stop_requested = False
        try:
            heard = self.voice.listen()
        except Exception as exc:
            raise MissingDependencyError(str(exc)) from exc
        return heard.strip()

    def handle_file(self, path: str) -> str:
        file_path = Path(path).expanduser()
        if not file_path.exists() or not file_path.is_file():
            raise UserInputError(f"File not found: {file_path}")
        content = file_path.read_text(encoding="utf-8", errors="ignore")[:FILE_CONTENT_PREVIEW_CHARS]
        prompt = f"File input from {file_path.name}: {content}"
        return self.handle_text(prompt)

    def play_last_response(self) -> str:
        response = self.current_session().last_response
        if not response:
            raise UserInputError("No response available to play.")
        try:
            return self.voice.speak(response)
        except Exception as exc:
            raise MissingDependencyError(str(exc)) from exc

    def query_memory(self, query: str, k: int = 5) -> List[MemoryItem]:
        return self.vector_memory.query(query, k=k)

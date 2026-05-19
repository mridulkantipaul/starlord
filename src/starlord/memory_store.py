"""File + vector memory (lightweight)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class MemoryItem:
    text: str


class FileMemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, item: MemoryItem) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(item.text.replace("\n", " ") + "\n")

    def list(self) -> List[MemoryItem]:
        if not self.path.exists():
            return []
        return [MemoryItem(text=line.strip()) for line in self.path.read_text(encoding="utf-8").splitlines()]


class SimpleVectorMemory:
    """Toy vector-like memory using token overlap scoring (no deps)."""

    def __init__(self) -> None:
        self.items: List[MemoryItem] = []

    def add(self, item: MemoryItem) -> None:
        self.items.append(item)

    def query(self, text: str, k: int = 5) -> List[MemoryItem]:
        query_tokens = set(text.lower().split())
        scored = []
        for item in self.items:
            tokens = set(item.text.lower().split())
            score = len(query_tokens & tokens)
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:k] if score > 0]

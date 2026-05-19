"""Memory interfaces (stub)."""

from dataclasses import dataclass
from typing import List


@dataclass
class MemoryItem:
    text: str


class MemoryStore:
    def add(self, item: MemoryItem) -> None:
        raise NotImplementedError

    def list(self) -> List[MemoryItem]:
        raise NotImplementedError


class InMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._items: List[MemoryItem] = []

    def add(self, item: MemoryItem) -> None:
        self._items.append(item)

    def list(self) -> List[MemoryItem]:
        return list(self._items)

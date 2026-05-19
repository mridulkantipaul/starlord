"""Simple task/reminder store."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Task:
    title: str
    due: datetime | None = None
    done: bool = False


class TaskStore:
    def __init__(self) -> None:
        self._tasks: List[Task] = []

    def add(self, task: Task) -> None:
        self._tasks.append(task)

    def list(self) -> List[Task]:
        return list(self._tasks)

    def toggle(self, idx: int) -> None:
        if 0 <= idx < len(self._tasks):
            self._tasks[idx].done = not self._tasks[idx].done

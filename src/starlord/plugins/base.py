"""Plugin base interface."""

from dataclasses import dataclass


@dataclass
class Plugin:
    name: str

    def setup(self) -> None:
        """Initialize plugin resources."""
        return None

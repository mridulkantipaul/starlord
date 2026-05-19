"""System tray support (Windows-first)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class Tray(QObject):
    show_requested = Signal()
    quit_requested = Signal()

    def __init__(self, icon: QIcon) -> None:
        super().__init__()
        self.tray = QSystemTrayIcon(icon)
        menu = QMenu()
        show_action = menu.addAction("Show Star Lord")
        quit_action = menu.addAction("Quit")
        show_action.triggered.connect(self.show_requested.emit)
        quit_action.triggered.connect(self.quit_requested.emit)
        self.tray.setContextMenu(menu)

    def show(self) -> None:
        self.tray.show()

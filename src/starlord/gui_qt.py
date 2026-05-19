"""Professional desktop GUI (PySide6/Qt)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from starlord.api.server import LocalAPIServer
from starlord.config.settings import Settings
from starlord.core.agent import Agent
from starlord.memory_store import FileMemoryStore, MemoryItem, SimpleVectorMemory
from starlord.plugins.manager import PluginManager
from starlord.settings_store import load_settings, save_settings
from starlord.system_tray import Tray
from starlord.tasks import Task, TaskStore


@dataclass
class ChatSession:
    name: str


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Star Lord")
        self.resize(1200, 800)

        self.settings = load_settings()
        self.agent = Agent(name=self.settings.agent_name)
        self.task_store = TaskStore()
        self.memory_file = FileMemoryStore(Path.home() / ".starlord" / "memory.txt")
        self.vector_memory = SimpleVectorMemory()
        self.plugins = PluginManager(Path(__file__).parent / "plugins")
        self.api = LocalAPIServer("127.0.0.1", 8765, self.agent.handle_input)
        self.api.start()

        self._init_ui()

    def _init_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)

        self.sessions = QListWidget()
        self.sessions.setFixedWidth(200)
        self.sessions.addItem("Default")

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.returnPressed.connect(self._send)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send)

        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(send_btn)
        chat_layout.addLayout(input_row)

        chat_panel = QWidget()
        chat_panel.setLayout(chat_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(chat_panel, "Chat")
        self.tabs.addTab(self._build_files(), "Files")
        self.tabs.addTab(self._build_code(), "Code")
        self.tabs.addTab(self._build_tasks(), "Tasks")
        self.tabs.addTab(self._build_plugins(), "Plugins")
        self.tabs.addTab(self._build_settings(), "Settings")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sessions)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setCentralWidget(root)

        # System tray
        self.tray = Tray(QIcon())
        self.tray.show_requested.connect(self.showNormal)
        self.tray.quit_requested.connect(self.close)
        self.tray.show()

    def _build_files(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(str(Path.home()))
        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(str(Path.home())))
        layout.addWidget(self.tree)
        return widget

    def _build_code(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Code Assistant"))
        self.code_input = QTextEdit()
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        run_btn = QPushButton("Analyze (stub)")
        run_btn.clicked.connect(self._run_code_assistant)
        layout.addWidget(self.code_input)
        layout.addWidget(run_btn)
        layout.addWidget(self.code_output)
        return widget

    def _build_tasks(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.task_list = QListWidget()
        self.task_entry = QLineEdit()
        self.task_entry.setPlaceholderText("New task...")
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_task)
        layout.addWidget(self.task_list)
        layout.addWidget(self.task_entry)
        layout.addWidget(add_btn)
        return widget

    def _build_plugins(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.plugin_list = QListWidget()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_plugins)
        layout.addWidget(self.plugin_list)
        layout.addWidget(refresh_btn)
        self._refresh_plugins()
        return widget

    def _build_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Agent Name"))
        self.agent_name = QLineEdit(self.settings.agent_name)
        layout.addWidget(self.agent_name)
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        return widget

    def _send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.chat.append(f"> {text}")
        response = self.agent.handle_input(text)
        self.chat.append(response)
        self.memory_file.add(MemoryItem(text=text))
        self.vector_memory.add(MemoryItem(text=text))

    def _run_code_assistant(self) -> None:
        code = self.code_input.toPlainText().strip()
        if not code:
            return
        self.code_output.setPlainText("Code assistant (stub): add static analysis here.")

    def _add_task(self) -> None:
        text = self.task_entry.text().strip()
        if not text:
            return
        self.task_entry.clear()
        self.task_store.add(Task(title=text))
        item = QListWidgetItem(text)
        self.task_list.addItem(item)

    def _refresh_plugins(self) -> None:
        self.plugin_list.clear()
        for plugin in self.plugins.discover():
            self.plugin_list.addItem(f"{plugin.name} ({plugin.module})")

    def _save_settings(self) -> None:
        self.settings.agent_name = self.agent_name.text().strip() or self.settings.agent_name
        save_settings(self.settings)
        QMessageBox.information(self, "Saved", "Settings saved.")

    def closeEvent(self, event) -> None:  # noqa: N802
        self.api.stop()
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

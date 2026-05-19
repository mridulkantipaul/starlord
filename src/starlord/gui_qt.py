"""Professional desktop GUI (PySide6/Qt)."""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from starlord.api.server import LocalAPIServer
from starlord.command_system import AgentCommandSystem
from starlord.core.agent import Agent
from starlord.memory_store import FileMemoryStore, SimpleVectorMemory
from starlord.plugins.manager import PluginManager
from starlord.settings_store import load_settings, save_settings
from starlord.system_tray import Tray
from starlord.tasks import Task, TaskStore

class MainWindow(QMainWindow):
    action_finished = Signal(str, str)
    action_failed = Signal(str, str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Star Lord")
        self.resize(1200, 800)

        self.settings = load_settings()
        self.agent = Agent(name=self.settings.agent_name)
        self.task_store = TaskStore()
        self.memory_file = FileMemoryStore(Path.home() / ".starlord" / "memory.txt")
        self.vector_memory = SimpleVectorMemory()
        self.command_system = AgentCommandSystem(
            agent=self.agent,
            settings=self.settings,
            memory_file=self.memory_file,
            vector_memory=self.vector_memory,
        )
        self.plugins = PluginManager(Path(__file__).parent / "plugins")
        self.api = LocalAPIServer("127.0.0.1", 8765, self.agent.handle_input)
        self.api.start()

        self.action_finished.connect(self._on_action_finished)
        self.action_failed.connect(self._on_action_failed)
        self._init_ui()

    def _init_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)

        self.sessions = QListWidget()
        self.sessions.setFixedWidth(200)
        self.sessions.addItem("Default")
        self.sessions.currentTextChanged.connect(self._switch_session)
        self.sessions.setCurrentRow(0)
        self.sessions.setAccessibleName("Session list")

        self.chat = QPlainTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setAccessibleName("Chat transcript")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.returnPressed.connect(self._send)
        self.input.setAccessibleName("Prompt input")
        self.input.setAccessibleDescription("Type your message and press Enter to send")

        self.listen_btn = QPushButton("Listen")
        self.listen_btn.clicked.connect(self._listen)
        self.listen_btn.setShortcut("Ctrl+L")
        self.listen_btn.setAccessibleName("Listen button")

        self.type_btn = QPushButton("Type")
        self.type_btn.clicked.connect(self.input.setFocus)
        self.type_btn.setShortcut("Ctrl+T")
        self.type_btn.setAccessibleName("Type mode button")

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setShortcut("Ctrl+.")
        self.stop_btn.setAccessibleName("Stop button")

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._play_last)
        self.play_btn.setShortcut("Ctrl+P")
        self.play_btn.setAccessibleName("Play response button")

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setShortcut("Ctrl+Return")
        self.send_btn.setAccessibleName("Send message button")

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.settings_tab))
        self.settings_btn.setAccessibleName("Open settings button")

        self.files_btn = QPushButton("File Explorer")
        self.files_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.files_tab))
        self.files_btn.setAccessibleName("Open file explorer button")

        self.memory_btn = QPushButton("Memory")
        self.memory_btn.clicked.connect(self._show_memory)
        self.memory_btn.setAccessibleName("Memory search button")

        self.plugins_btn = QPushButton("Plugins")
        self.plugins_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.plugins_tab))
        self.plugins_btn.setAccessibleName("Open plugins button")

        chat_layout = QVBoxLayout()
        header = QLabel("🤖 Star Lord  |  🧑 Operator")
        chat_layout.addWidget(header)

        tools_row = QHBoxLayout()
        for btn in (
            self.listen_btn,
            self.type_btn,
            self.stop_btn,
            self.play_btn,
            self.files_btn,
            self.memory_btn,
            self.plugins_btn,
            self.settings_btn,
        ):
            tools_row.addWidget(btn)
        chat_layout.addLayout(tools_row)
        chat_layout.addWidget(self.chat)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        self.open_file_btn = QPushButton("Attach File")
        self.open_file_btn.clicked.connect(self._open_file)
        input_row.addWidget(self.open_file_btn)
        input_row.addWidget(self.send_btn)
        chat_layout.addLayout(input_row)

        chat_panel = QWidget()
        chat_panel.setLayout(chat_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(chat_panel, "Chat")
        self.files_tab = self._build_files()
        self.tabs.addTab(self.files_tab, "Files")
        self.tabs.addTab(self._build_code(), "Code")
        self.tabs.addTab(self._build_tasks(), "Tasks")
        self.plugins_tab = self._build_plugins()
        self.tabs.addTab(self.plugins_tab, "Plugins")
        self.settings_tab = self._build_settings()
        self.tabs.addTab(self.settings_tab, "Settings")

        splitter = QSplitter(Qt.Horizontal)
        session_panel = QWidget()
        session_layout = QVBoxLayout(session_panel)
        session_layout.addWidget(QLabel("Sessions"))
        session_layout.addWidget(self.sessions)
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self._new_session)
        session_layout.addWidget(self.new_session_btn)
        splitter.addWidget(session_panel)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setCentralWidget(root)

        # System tray
        self.tray = Tray(QIcon())
        self.tray.show_requested.connect(self.showNormal)
        self.tray.quit_requested.connect(self.close)
        self.tray.show()
        self.statusBar().showMessage("Ready. System tray active.")

    def _build_files(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(str(Path.home()))
        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(str(Path.home())))
        self.tree.doubleClicked.connect(self._from_tree_selection)
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
            self.statusBar().showMessage("Type a message first.", 3000)
            return
        self.input.clear()
        self.chat.appendPlainText(f"> {text}")
        self._run_action("send", lambda: self.command_system.handle_text(text))

    def _listen(self) -> None:
        self._run_action("listen", self.command_system.handle_voice)

    def _stop(self) -> None:
        message = self.command_system.request_stop()
        self.statusBar().showMessage(message, 2000)

    def _play_last(self) -> None:
        self._run_action("play", self.command_system.play_last_response)

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input file")
        if not path:
            return
        self._run_action("file", lambda: self.command_system.handle_file(path))

    def _from_tree_selection(self, index) -> None:
        path = self.fs_model.filePath(index)
        if Path(path).is_file():
            self._run_action("file", lambda: self.command_system.handle_file(path))

    def _show_memory(self) -> None:
        query = self.input.text().strip()
        if not query:
            self.statusBar().showMessage("Enter text in the input box to search memory.", 3000)
            return
        items = self.command_system.query_memory(query)
        if not items:
            self.chat.appendPlainText("[memory] No matches.")
            return
        self.chat.appendPlainText("[memory] Matches:")
        for item in items:
            self.chat.appendPlainText(f" - {item.text}")

    def _run_action(self, action: str, fn: Callable[[], str]) -> None:
        self._set_controls_enabled(False)
        self.statusBar().showMessage(f"Running {action}...")

        def _worker() -> None:
            try:
                result = fn()
                self.action_finished.emit(action, result)
            except Exception as exc:
                self.action_failed.emit(action, exc.__class__.__name__, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_action_finished(self, action: str, result: str) -> None:
        if action == "listen":
            self.input.setText(result)
            self.statusBar().showMessage("Voice captured. Edit or send the message.", 3000)
        elif action == "play":
            self.statusBar().showMessage(f"Audio generated: {result}", 4000)
        else:
            self.chat.appendPlainText(result)
            self.statusBar().showMessage(f"{action.title()} complete.", 3000)
        self._set_controls_enabled(True)

    def _on_action_failed(self, action: str, error_type: str, error: str) -> None:
        self._set_controls_enabled(True)
        self.statusBar().showMessage(f"{action.title()} failed.", 3000)
        friendly = "Please check your settings and try again."
        if error_type == "MissingDependencyError":
            friendly = "Missing optional dependency. Install the required voice package and try again."
        elif error_type == "UserInputError":
            friendly = "Selected file could not be loaded. Choose a different file and retry."
        if action == "send":
            self.chat.appendPlainText("[assistant] Sorry, I couldn't process that request.")
        QMessageBox.warning(self, "Action Error", friendly)

    def _set_controls_enabled(self, enabled: bool) -> None:
        for btn in (
            self.listen_btn,
            self.type_btn,
            self.play_btn,
            self.send_btn,
            self.open_file_btn,
            self.files_btn,
            self.memory_btn,
            self.plugins_btn,
            self.settings_btn,
            self.new_session_btn,
        ):
            btn.setEnabled(enabled)
        self.stop_btn.setEnabled(True)

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
        self.statusBar().showMessage("Settings saved.", 3000)

    def _switch_session(self, name: str) -> None:
        if not name or not hasattr(self, "chat"):
            return
        session = self.command_system.switch_session(name)
        self.chat.clear()
        if session.history:
            self.chat.appendPlainText("\n".join(session.history))

    def _new_session(self) -> None:
        session = self.command_system.create_session("")
        self.sessions.addItem(session.name)
        self.sessions.setCurrentRow(self.sessions.count() - 1)
        self.chat.clear()
        self.statusBar().showMessage(f"Created {session.name}.", 3000)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.api.stop()
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

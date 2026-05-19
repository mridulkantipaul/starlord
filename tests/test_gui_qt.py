"""Basic GUI interaction tests for Qt frontend."""

from __future__ import annotations

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

try:
    from PySide6.QtWidgets import QApplication
except (ImportError, ModuleNotFoundError, OSError) as exc:  # pragma: no cover - environment dependent
    pytest.skip(f"Qt runtime not available: {exc}", allow_module_level=True)

import starlord.gui_qt as gui_qt


class _SignalStub:
    def connect(self, _callback) -> None:
        return None


class _TrayStub:
    def __init__(self, _icon) -> None:
        self.show_requested = _SignalStub()
        self.quit_requested = _SignalStub()

    def show(self) -> None:
        return None


class _ServerStub:
    def __init__(self, *_args, **_kwargs) -> None:
        return None

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


def _wait_for_events(app: QApplication, cycles: int = 20) -> None:
    for _ in range(cycles):
        app.processEvents()
        time.sleep(0.01)


def _get_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_loads_and_core_buttons_exist(monkeypatch):
    monkeypatch.setattr(gui_qt, "Tray", _TrayStub)
    monkeypatch.setattr(gui_qt, "LocalAPIServer", _ServerStub)
    app = _get_app()
    window = gui_qt.MainWindow()

    _wait_for_events(app)
    assert window.windowTitle() == "Star Lord"
    for attr in ("listen_btn", "type_btn", "stop_btn", "play_btn", "send_btn", "memory_btn", "plugins_btn", "settings_btn"):
        assert getattr(window, attr).isEnabled()
    assert window.agent_state_label.text() == "State: Ready"
    assert window.session_indicator_label.text() == "Session: Default"

    window.close()


def test_navigation_buttons_switch_tabs_and_type_mode(monkeypatch):
    monkeypatch.setattr(gui_qt, "Tray", _TrayStub)
    monkeypatch.setattr(gui_qt, "LocalAPIServer", _ServerStub)
    app = _get_app()
    window = gui_qt.MainWindow()

    window.settings_btn.click()
    _wait_for_events(app)
    assert window.tabs.currentWidget() is window.settings_tab
    assert "Settings panel ready." in window.statusBar().currentMessage()

    window.plugins_btn.click()
    _wait_for_events(app)
    assert window.tabs.currentWidget() is window.plugins_tab
    assert "Plugin manager ready." in window.statusBar().currentMessage()

    window.files_btn.click()
    _wait_for_events(app)
    assert window.tabs.currentWidget() is window.files_tab
    assert "File explorer ready." in window.statusBar().currentMessage()

    window.type_btn.click()
    _wait_for_events(app)
    assert window.agent_state_label.text() == "State: Typing"
    assert "Type mode enabled." in window.statusBar().currentMessage()

    window.close()


def test_send_button_dispatches_response(monkeypatch):
    monkeypatch.setattr(gui_qt, "Tray", _TrayStub)
    monkeypatch.setattr(gui_qt, "LocalAPIServer", _ServerStub)
    app = _get_app()
    window = gui_qt.MainWindow()
    monkeypatch.setattr(window.command_system, "handle_text", lambda text: f"stub-response:{text}")

    window.input.setText("hello")
    window.send_btn.click()
    _wait_for_events(app)

    assert "> hello" in window.chat.toPlainText()
    assert "stub-response:hello" in window.chat.toPlainText()
    assert window.agent_state_label.text() == "State: Ready"
    window.close()


def test_send_button_error_shows_feedback(monkeypatch):
    monkeypatch.setattr(gui_qt, "Tray", _TrayStub)
    monkeypatch.setattr(gui_qt, "LocalAPIServer", _ServerStub)
    app = _get_app()
    window = gui_qt.MainWindow()

    messages: list[str] = []
    monkeypatch.setattr(
        gui_qt.QMessageBox,
        "warning",
        lambda _self, _title, msg: messages.append(msg),
    )
    def _raise_runtime_error(_text: str) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(window.command_system, "handle_text", _raise_runtime_error)

    window.input.setText("hello")
    window.send_btn.click()
    _wait_for_events(app)

    assert messages
    assert "Please check your settings" in messages[0]
    assert "Sorry, I couldn't process that request." in window.chat.toPlainText()
    assert window.agent_state_label.text() == "State: Error"
    window.close()


def test_memory_button_empty_query_shows_feedback(monkeypatch):
    monkeypatch.setattr(gui_qt, "Tray", _TrayStub)
    monkeypatch.setattr(gui_qt, "LocalAPIServer", _ServerStub)
    app = _get_app()
    window = gui_qt.MainWindow()

    window.input.clear()
    window.memory_btn.click()
    _wait_for_events(app)

    assert "Enter text in the input box to search memory." in window.statusBar().currentMessage()
    window.close()

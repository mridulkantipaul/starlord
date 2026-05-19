"""Basic GUI interaction tests for Qt frontend."""

from __future__ import annotations

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

try:
    from PySide6.QtWidgets import QApplication
except Exception as exc:  # pragma: no cover - environment dependent
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
    window.close()

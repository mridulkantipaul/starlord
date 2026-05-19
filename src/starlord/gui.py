"""Desktop GUI for Star Lord (Tkinter)."""

from __future__ import annotations

import tkinter as tk
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from typing import Callable

from starlord.command_system import AgentCommandSystem
from starlord.config.settings import Settings
from starlord.core.agent import Agent
from starlord.memory_store import FileMemoryStore, SimpleVectorMemory


class StarLordGUI:
    def __init__(self) -> None:
        self.agent = Agent()
        self.command_system = AgentCommandSystem(
            agent=self.agent,
            settings=Settings(),
            memory_file=FileMemoryStore(Path.home() / ".starlord" / "memory.txt"),
            vector_memory=SimpleVectorMemory(),
        )
        self.root = tk.Tk()
        self.root.title("Star Lord")
        self.root.geometry("1080x640")
        self.root.minsize(820, 520)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.main_panel = tk.Frame(self.root)
        self.main_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=10)
        self.main_panel.columnconfigure(0, weight=1)
        self.main_panel.rowconfigure(1, weight=1)

        self.header = tk.Frame(self.main_panel)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(self.header, text="STAR LORD // COMMAND DECK", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(self.header, text="🤖 Star Lord  |  🧑 Operator  |  Tk fallback online").grid(row=1, column=0, sticky="w")

        self.output = scrolledtext.ScrolledText(self.main_panel, wrap=tk.WORD, state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew")

        self.input_frame = tk.Frame(self.main_panel)
        self.input_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.input_frame.columnconfigure(0, weight=1)

        self.entry = tk.Entry(self.input_frame)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self.on_send)

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.on_send)
        self.send_btn.grid(row=0, column=1, padx=(8, 0))

        self.sidebar = tk.Frame(self.root)
        self.sidebar.grid(row=0, column=1, sticky="ns", padx=(6, 10), pady=10)

        tk.Label(self.sidebar, text="🤖", font=("Segoe UI Emoji", 28)).grid(row=0, column=0, pady=(4, 0))
        self.agent_name_label = tk.Label(self.sidebar, text=self.agent.name, font=("Segoe UI", 12, "bold"))
        self.agent_name_label.grid(row=1, column=0, pady=(0, 4))
        self.agent_state_label = tk.Label(self.sidebar, text="State: Ready")
        self.agent_state_label.grid(row=2, column=0, pady=(0, 2))
        self.system_label = tk.Label(self.sidebar, text="System: local mode")
        self.system_label.grid(row=3, column=0, pady=(0, 2))
        self.session_label = tk.Label(self.sidebar, text="Session: Default")
        self.session_label.grid(row=4, column=0, pady=(0, 8))

        self.listen_btn = tk.Button(self.sidebar, text="Listen", command=self.on_listen)
        self.type_btn = tk.Button(self.sidebar, text="Type", command=self.on_type_mode)
        self.stop_btn = tk.Button(self.sidebar, text="Stop", command=self.on_stop)
        self.play_btn = tk.Button(self.sidebar, text="Play", command=self.on_play)
        self.settings_btn = tk.Button(self.sidebar, text="Settings", command=self.on_settings)
        self.files_btn = tk.Button(self.sidebar, text="File Explorer", command=self.on_file)
        self.memory_btn = tk.Button(self.sidebar, text="Memory", command=self.on_memory)
        self.plugins_btn = tk.Button(self.sidebar, text="Plugins", command=self.on_plugins)

        for idx, btn in enumerate(
            (
                self.listen_btn,
                self.type_btn,
                self.stop_btn,
                self.play_btn,
                self.files_btn,
                self.memory_btn,
                self.plugins_btn,
                self.settings_btn,
            ),
            start=5,
        ):
            btn.grid(in_=self.sidebar, row=idx, column=0, sticky="ew", padx=2, pady=2)

        self.status_var = tk.StringVar(value="Ready. Keyboard: Enter to send.")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        self._write("Star Lord online (GUI). Type your message and press Enter.")

    def _write(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.yview(tk.END)

    def _run_async(self, fn: Callable[[], str], action_name: str) -> None:
        self._set_agent_state(action_name.title())
        self.status_var.set(f"Running {action_name}...")
        self._set_controls(False)

        def worker() -> None:
            try:
                result = fn()
            except Exception as exc:
                self.root.after(0, lambda: self._handle_error(action_name, exc.__class__.__name__, str(exc)))
                return
            self.root.after(0, lambda: self._handle_success(action_name, result))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_success(self, action_name: str, result: str) -> None:
        if action_name == "listen":
            self.entry.delete(0, tk.END)
            self.entry.insert(0, result)
            self.status_var.set("Voice captured. Press Send to continue.")
        elif action_name == "play":
            self.status_var.set(f"Audio generated: {result}")
        else:
            self._write(result)
            self.status_var.set(f"{action_name.title()} complete.")
        self._set_agent_state("Ready")
        self._set_controls(True)

    def _handle_error(self, action_name: str, error_type: str, _error: str) -> None:
        self._set_controls(True)
        self._set_agent_state("Error")
        self.status_var.set(f"{action_name.title()} failed.")
        friendly = "Please check your settings and try again."
        if error_type == "MissingDependencyError":
            friendly = "Missing optional dependency. Install the required voice package and retry."
        elif error_type == "UserInputError":
            friendly = "Selected file could not be loaded. Choose another file and retry."
        if action_name == "send":
            self._write("[assistant] Sorry, I couldn't process that request.")
        messagebox.showwarning("Action Error", friendly)

    def _set_controls(self, enabled: bool) -> None:
        for widget in (
            self.listen_btn,
            self.type_btn,
            self.play_btn,
            self.send_btn,
            self.settings_btn,
            self.files_btn,
            self.memory_btn,
            self.plugins_btn,
        ):
            widget.configure(state=("normal" if enabled else "disabled"))
        self.stop_btn.configure(state="normal")

    def on_send(self, event=None) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            self.status_var.set("Type a message first.")
            return
        self.entry.delete(0, tk.END)
        self._write(f"> {user_text}")
        self._run_async(lambda: self.command_system.handle_text(user_text), "send")

    def on_listen(self) -> None:
        self._run_async(self.command_system.handle_voice, "listen")

    def on_type_mode(self) -> None:
        self.entry.focus_set()
        self._set_agent_state("Typing")
        self.status_var.set("Type mode enabled.")

    def on_stop(self) -> None:
        self._set_agent_state("Stopped")
        self.status_var.set(self.command_system.request_stop())

    def on_play(self) -> None:
        self._run_async(self.command_system.play_last_response, "play")

    def on_file(self) -> None:
        file_path = filedialog.askopenfilename(title="Select input file")
        if not file_path:
            return
        self._run_async(lambda: self.command_system.handle_file(file_path), "file")

    def on_memory(self) -> None:
        query = self.entry.get().strip()
        if not query:
            self.status_var.set("Enter text to search memory.")
            return
        self._set_agent_state("Memory")
        items = self.command_system.query_memory(query)
        if not items:
            self._write("[memory] No matches.")
            self.status_var.set("No memory matches found.")
            self._set_agent_state("Ready")
            return
        self._write("[memory] Matches:")
        for item in items:
            self._write(f" - {item.text}")
        self.status_var.set(f"Memory returned {len(items)} result(s).")
        self._set_agent_state("Ready")

    def on_settings(self) -> None:
        self._set_agent_state("Ready")
        self.status_var.set("Settings panel stub opened.")
        self._write("[settings] Agent/profile settings panel opened (stub).")

    def on_plugins(self) -> None:
        self._set_agent_state("Ready")
        self.status_var.set("Plugin manager stub opened.")
        self._write("[plugins] Plugin manager opened (stub).")

    def _set_agent_state(self, state: str) -> None:
        self.agent_state_label.configure(text=f"State: {state}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    StarLordGUI().run()


if __name__ == "__main__":
    main()

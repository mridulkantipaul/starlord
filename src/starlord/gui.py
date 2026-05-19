"""Desktop GUI for Star Lord (Tkinter)."""

from __future__ import annotations

import tkinter as tk
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
        self.root.geometry("900x560")
        self.root.minsize(760, 480)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.toolbar = tk.Frame(self.root)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.toolbar.columnconfigure(9, weight=1)

        self.listen_btn = tk.Button(self.toolbar, text="Listen", command=self.on_listen)
        self.type_btn = tk.Button(self.toolbar, text="Type", command=self.on_type_mode)
        self.stop_btn = tk.Button(self.toolbar, text="Stop", command=self.on_stop)
        self.play_btn = tk.Button(self.toolbar, text="Play", command=self.on_play)
        self.settings_btn = tk.Button(self.toolbar, text="Settings", command=lambda: self._write("[settings] Open settings panel (stub)"))
        self.files_btn = tk.Button(self.toolbar, text="File Explorer", command=self.on_file)
        self.memory_btn = tk.Button(self.toolbar, text="Memory", command=self.on_memory)
        self.plugins_btn = tk.Button(self.toolbar, text="Plugins", command=lambda: self._write("[plugins] Open plugins panel (stub)"))

        for idx, btn in enumerate(
            (
                self.listen_btn,
                self.type_btn,
                self.stop_btn,
                self.play_btn,
                self.settings_btn,
                self.files_btn,
                self.memory_btn,
                self.plugins_btn,
            )
        ):
            btn.grid(row=0, column=idx, padx=2, pady=2)

        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.input_frame.columnconfigure(0, weight=1)

        self.entry = tk.Entry(self.input_frame)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self.on_send)

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.on_send)
        self.send_btn.grid(row=0, column=1, padx=(8, 0))

        self.status_var = tk.StringVar(value="Ready. Keyboard: Enter to send.")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._write("Star Lord online (GUI). Type your message and press Enter.")

    def _write(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.yview(tk.END)

    def _run_async(self, fn: Callable[[], str], action_name: str) -> None:
        self.status_var.set(f"Running {action_name}...")
        self._set_controls(False)

        def worker() -> None:
            try:
                result = fn()
            except Exception as exc:
                self.root.after(0, lambda: self._handle_error(action_name, str(exc)))
                return
            self.root.after(0, lambda: self._handle_success(action_name, result))

        import threading

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
        self._set_controls(True)

    def _handle_error(self, action_name: str, error: str) -> None:
        self._set_controls(True)
        self.status_var.set(f"{action_name.title()} failed.")
        messagebox.showwarning("Action Error", f"{action_name.title()} failed:\n{error}")

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
        self.status_var.set("Type mode enabled.")

    def on_stop(self) -> None:
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
        items = self.command_system.query_memory(query)
        if not items:
            self._write("[memory] No matches.")
            return
        self._write("[memory] Matches:")
        for item in items:
            self._write(f" - {item.text}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    StarLordGUI().run()


if __name__ == "__main__":
    main()

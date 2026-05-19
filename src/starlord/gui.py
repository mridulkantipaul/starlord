"""Desktop GUI for Star Lord (Tkinter)."""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext

from starlord.core.agent import Agent


class StarLordGUI:
    def __init__(self) -> None:
        self.agent = Agent()
        self.root = tk.Tk()
        self.root.title("Star Lord")
        self.root.geometry("640x480")

        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled")
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.entry = tk.Entry(self.input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.on_send)

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=(8, 0))

        self._write("Star Lord online (GUI). Type your message and press Enter.")

    def _write(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.yview(tk.END)

    def on_send(self, event=None) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        self._write(f"> {user_text}")
        response = self.agent.handle_input(user_text)
        self._write(response)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    StarLordGUI().run()


if __name__ == "__main__":
    main()

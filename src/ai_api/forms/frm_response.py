# forms/frm_response.py
# Response form for displaying AI responses


"""MainFrame for <application>."""

import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from psiutils.buttons import ButtonFrame
from psiutils.constants import PAD
from psiutils.utilities import window_resize

from ai_api.config import read_config
from ai_api.constants import APP_TITLE, EDITOR
from ai_api.main_menu import MainMenu

FRAME_TITLE = APP_TITLE


class ResponseFrame:
    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.config = read_config()
        self.response_file_path = ""

        # tk variables
        self.response = tk.StringVar()

        self.show()

    def show(self):
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)

        root.bind("<Control-x>", self._dismiss)
        # root.bind("<Control-o>", self._process)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        """Build the main frame with a scrollable text widget."""
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.text = self._create_text_widget(frame)
        self._add_vertical_scrollbar(frame, self.text)
        self.text.insert("1.0", self.response.get())

        return frame

    def _create_text_widget(self, parent: ttk.Frame) -> tk.Text:
        """Create and grid the main text widget."""
        text = tk.Text(parent)
        text.grid(row=0, column=0, sticky=tk.NSEW)
        text.bind("<Control-a>", self._select_all)
        return text

    def _add_vertical_scrollbar(
        self, parent: ttk.Frame, widget: tk.Text
    ) -> tk.Scrollbar:
        """Attach a vertical scrollbar to the given widget."""
        scrollbar = tk.Scrollbar(
            parent, orient=tk.VERTICAL, command=widget.yview
        )
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        widget.configure(yscrollcommand=scrollbar.set)
        return scrollbar

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("open", self._open_file),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _select_all(self, event: tk.Event) -> str:
        """Select all text in the Text widget."""
        event.widget.tag_add("sel", "1.0", "end")
        event.widget.mark_set("insert", "end")
        event.widget.see("insert")
        return "break"  # Prevents default behaviour

    def _open_file(self, *args) -> None:
        if self.response_file_path:
            subprocess.call([EDITOR, str(self.response_file_path)])

    def _dismiss(self, *args) -> None:
        self.root.destroy()

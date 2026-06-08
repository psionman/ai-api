"""AppFrame for AI Interface."""

import subprocess
import tkinter as tk
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import clipboard
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD, TXT_FILE_TYPES, Pad
from psiutils.utilities import window_resize
from psiutils.widgets import WaitCursor

from ai_api.claude import prompt_claude
from ai_api.config import read_config
from ai_api.constants import APP_TITLE, USER_DATA_DIR
from ai_api.forms.frm_response import ResponseFrame
from ai_api.main_menu import MainMenu
from ai_api.open_ai import prompt_chatgpt
from ai_api.system_text import SYSTEM_PROMPTS
from ai_api.text import Text

txt = Text()

FRAME_HEIGHT = 4000
HORIZONTAL_SASH_COUNT = 1
SEPARATOR = "=" * 75

OUTPUT_DIR = Path(USER_DATA_DIR, "ai_output")
OUTPUT_DIR.mkdir(exist_ok=True)
QUESTION_DIR = Path(USER_DATA_DIR, "ai_input")
QUESTION_DIR.mkdir(exist_ok=True)

providers = ["Claude", "ChatGPT"]
PROVIDER_HANDLERS: dict[str, Callable[[str, str], str]] = {
    "Claude": prompt_claude,
    "ChatGPT": prompt_chatgpt,
}
domains = list(SYSTEM_PROMPTS.keys())


class AppFrame:
    """Create AppFrame for AI Interface application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = read_config()

        todays_question_file = Path(
            QUESTION_DIR, f"question_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        # tk variables
        self.question_file = tk.StringVar(value=todays_question_file)
        self.provider = tk.StringVar(value="Claude")
        self.domain = tk.StringVar(value="Technical")

        self._show()

    def _show(self):
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(APP_TITLE)

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-o>", self._send)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        self.main_frame = self._main_frame(root)
        self.main_frame.grid(
            row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD
        )

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        row = 0
        file_frame = self._file_frame(frame)
        file_frame.grid(row=row, column=0, sticky=tk.EW)

        row += 1
        self.domain_frame = self._domain_frame(frame)
        self.domain_frame.grid(row=row, column=0, sticky=tk.NSEW)

        row += 1
        provider_frame = self._provider_frame(frame)
        provider_frame.grid(row=row, column=0, sticky=tk.EW)

        row += 1
        frame.rowconfigure(row, weight=1)
        question_frame = self._question_frame(frame)
        question_frame.grid(row=row, column=0, sticky=tk.NSEW)

        return frame

    def _provider_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master, relief=tk.SUNKEN)

        row = 0
        for column, provider in enumerate(providers):
            radio = ttk.Radiobutton(
                frame, text=provider, variable=self.provider, value=provider
            )
            radio.grid(row=row, column=column, sticky=tk.E, padx=PAD, pady=PAD)
        return frame

    def _file_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master, relief=tk.SUNKEN)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="Question file")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.question_file)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, "open", self._get_question_file)
        button.grid(row=row, column=2, padx=PAD, pady=Pad.S)

        button = IconButton(
            frame, txt.CREATE, "create", self._create_question_file
        )
        button.grid(row=row, column=3, padx=PAD, pady=Pad.S)

        return frame

    def _domain_frame(self, master: tk.Frame) -> tk.PanedWindow:
        frame = ttk.Frame(master, relief=tk.SUNKEN)

        row = 0
        for column, domain in enumerate(domains):
            radio = ttk.Radiobutton(
                frame, text=domain, variable=self.domain, value=domain
            )
            radio.grid(row=row, column=column, sticky=tk.E, padx=PAD, pady=PAD)
        return frame

    def _question_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master, relief=tk.SUNKEN)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.text = self._create_text_widget(frame)
        self._add_vertical_scrollbar(frame, self.text)
        return frame

    def _create_text_widget(self, parent: ttk.Frame) -> tk.Text:
        """Create and grid the main text widget."""
        text = tk.Text(parent)
        text.grid(row=0, column=0, sticky=tk.NSEW)
        text.bind("<KeyRelease>", self._value_changed)
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
            frame.icon_button("send", self._send, True),
            frame.icon_button("paste", self._paste),
            frame.icon_button("open", self._from_file, text="From file"),
            frame.icon_button("clear", self._clear),
            frame.icon_button("close", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _value_changed(self, *args) -> bool:
        """
        Determine whether any configuration value has changed.
        """
        text = self.text.get("1.0", tk.END).replace("\n", "")
        enable = True if text else False
        self.button_frame.enable(enable)

    def _send(self, *args) -> None:
        """Send prompt to AI provider and display response."""
        system = SYSTEM_PROMPTS[self.domain.get()]
        prompt = self.text.get("1.0", tk.END)
        file_path = self._build_file_path(prompt)

        try:
            with WaitCursor(self.root):
                response = self._get_response(system, prompt)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self._display_response(response, file_path)
        self._save_response(prompt, response, file_path)
        self._add_separator_to_question()

    def _display_response(self, response: str, file_path: Path) -> None:
        """Create and show a response frame."""
        frm = ResponseFrame(self)
        frm.response.set(response)
        frm.response_file_path = file_path
        frm.show()

    def _build_file_path(self, prompt: str) -> Path:
        """Build a timestamped file path from the prompt."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = self._slugify(prompt.strip())
        return OUTPUT_DIR / f"{timestamp}_{slug}.md"

    @staticmethod
    def _slugify(text: str, max_len: int = 20) -> str:
        """Create a truncated, filesystem-safe slug."""
        truncated = (
            f"{text[:max_len]}...{text[-max_len:]}"
            if len(text) > max_len * 2
            else text
        )
        return truncated.replace(" ", "_").replace("/", "-")

    def _get_response(self, system: str, prompt: str) -> str:
        """Dispatch prompt to the selected AI provider."""
        provider = self.provider.get()
        handler = PROVIDER_HANDLERS.get(provider)
        if handler is None:
            raise ValueError(f"Unknown provider: {provider}")
        return handler(system, prompt)

    def _save_response(
        self, prompt: str, response: str, file_path: Path
    ) -> None:
        """Persist prompt and response to a Markdown file."""
        file_path.write_text(
            f"# Prompt\n{prompt}\n\n{SEPARATOR}\n"
            f"# Response\n{response}\n\n{SEPARATOR}\n"
        )

    def _get_question_file(self, *args) -> None:
        initialfile = self.question_file.get()

        initialdir = Path(initialfile).parent if initialfile else QUESTION_DIR
        question_file = filedialog.askopenfilename(
            initialdir=initialdir,
            initialfile=initialfile,
            filetypes=TXT_FILE_TYPES,
        )
        if question_file:
            self.question_file.set(question_file)

    def _paste(self, *args) -> None:
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", clipboard.paste())
        self._value_changed()

    def _select_all(self, event: tk.Event) -> str:
        """Select all text in the Text widget."""
        event.widget.tag_add("sel", "1.0", "end")
        event.widget.mark_set("insert", "end")
        event.widget.see("insert")
        return "break"  # Prevents default behaviour

    def _from_file(self, *args) -> None:
        try:
            with open(self.question_file.get()) as f_question:
                text = self._get_last_question(f_question.read())
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            text = ""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self._value_changed()

    def _get_last_question(self, text: str) -> str:
        data = text.split("\n")
        last_question = []
        for line in reversed(data):
            if line == SEPARATOR:
                break
            last_question.append(line)
        return "\n".join(reversed(last_question))

    def _add_separator_to_question(self, *args) -> None:
        with open(self.question_file.get(), "a") as f_question:
            f_question.write(SEPARATOR + "\n")

    def _create_question_file(self, *args) -> None:
        try:
            with open(self.question_file.get(), "w") as f_question:
                f_question.write("")
                subprocess.call(["kate", str(self.question_file.get())])
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Failed to create file: {e}")

    def _clear(self, *args) -> None:
        self.text.delete("1.0", tk.END)
        self._value_changed()

    def _dismiss(self, *args) -> None:
        self.root.destroy()

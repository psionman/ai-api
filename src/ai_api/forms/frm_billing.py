"""BillingFrame for AI Interface."""

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD, WidgetState
from psiutils.utilities import window_resize

from ai_api.config import read_config
from ai_api.constants import APP_TITLE
from ai_api.models import MODELS
from ai_api.text import Text

txt = Text()

FRAME_TITLE = f"{APP_TITLE} - Billing"
DEFAULT_GEOMETRY = "100x100"
DATETIME_FORMAT = "%d %b %Y at %H:%M"
COST_FORMAT = ".2f"


class BillingFrame:
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()

        # tk variables
        self.provider = tk.StringVar()
        self.input_cost = tk.StringVar(value="0.00")
        self.output_cost = tk.StringVar(value="0.00")
        self.balance = tk.StringVar(value="0.00")
        self.last_updated = tk.StringVar(
            value=datetime.now().strftime(DATETIME_FORMAT)
        )

        self.show()
        self._update_provider()

    def show(self) -> None:
        root = self.root
        try:
            root.geometry(self.config.geometry[Path(__file__).stem])
        except KeyError:
            root.geometry(DEFAULT_GEOMETRY)
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )

        root.bind("<Control-x>", self._dismiss)

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
        frame = ttk.Frame(master)
        # frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        provider_frame = self._provider_frame(frame)
        provider_frame.grid(row=row, column=0, sticky=tk.EW)

        row += 1
        details_frame = self._details_frame(frame)
        details_frame.grid(row=row, column=0, sticky=tk.EW)

        return frame

    def _provider_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        row = 0
        for column, provider in enumerate(list(MODELS)):
            if column == 0:
                self.provider.set(provider)
            radio = ttk.Radiobutton(
                frame,
                text=provider,
                variable=self.provider,
                value=provider,
                command=self._update_provider,
            )
            radio.grid(row=row, column=column, sticky=tk.W, padx=PAD, pady=PAD)
        return frame

    def _details_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        row = 0
        label = ttk.Label(frame, text="Costs in $/M tokens")
        label.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Input cost")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.input_cost,
            justify="right",
            width=7,
        )
        entry.grid(row=row, column=1, sticky=tk.W, padx=PAD)

        label = ttk.Label(frame, text="Output cost")
        label.grid(row=row, column=2, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.output_cost,
            justify="right",
            width=7,
        )
        entry.grid(row=row, column=3, sticky=tk.W, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Balance")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.balance,
            justify="right",
            width=7,
        )
        entry.grid(row=row, column=1, sticky=tk.W, padx=PAD)

        label = ttk.Label(frame, text="Last updated")
        label.grid(row=row, column=2, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.last_updated,
            state=WidgetState.READONLY,
        )
        entry.grid(row=row, column=3, sticky=tk.W, padx=PAD)

        button = IconButton(frame, txt.SAVE, "save", self._update_provider)
        button.grid(row=row, column=4, sticky=tk.W, padx=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("build", self._process, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _update_provider(self) -> None:
        provider = MODELS[self.provider.get()]
        self.input_cost.set(f"{provider.costs.input:{COST_FORMAT}}")
        self.output_cost.set(f"{provider.costs.output:{COST_FORMAT}}")

    def _process(self, *args) -> None: ...

    def _dismiss(self, *args) -> None:
        self.root.destroy()

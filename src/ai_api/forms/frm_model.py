# forms/model.py


import tkinter as tk
from tkinter import TclError, ttk

from psiutils.buttons import ButtonFrame
from psiutils.constants import PAD, Mode, Status, WidgetState
from psiutils.utilities import geometry, window_resize

from ai_api.config import read_config
from ai_api.models import Model, UsageCosts, save_model
from ai_api.text import Text

txt = Text()
FRAME_TITLE = " Model edit"


class ModelEditFrame:
    def __init__(
        self, parent, mode: int, provider: str, model: Model = None
    ) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()
        self.mode = mode

        self.status = Status.NULL

        if not model:
            model = None

        self.model = model

        # tk variables
        self.provider = tk.StringVar(value=provider)
        self.name = tk.StringVar(value=model.name if model else "")
        self.model_name = tk.StringVar(value=model.model if model else "")
        self.input_cost = tk.DoubleVar(
            value=model.costs.input if model else 0.00
        )
        self.output_cost = tk.DoubleVar(
            value=model.costs.output if model else 0.00
        )

        # Trace
        self.name.trace_add("write", self._check_value_changed)
        self.model_name.trace_add("write", self._check_value_changed)
        self.input_cost.trace_add("write", self._check_value_changed)
        self.output_cost.trace_add("write", self._check_value_changed)

        self._show()

    def _show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(FRAME_TITLE)
        root.transient(self.parent.root)
        root.bind("<Control-x>", self._dismiss)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        state = (
            WidgetState.NORMAL
            if self.mode in (Mode.EDIT, Mode.NEW)
            else WidgetState.READONLY
        )
        row = 0
        frame.rowconfigure(row, weight=1)
        fields_frame = self._fields_frame(frame, state)
        fields_frame.grid(
            row=row, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD
        )

        row += 1
        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(
            row=row, column=0, columnspan=4, sticky=tk.EW, padx=PAD, pady=PAD
        )
        return frame

    def _fields_frame(self, master: tk.Frame, state: WidgetState) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(99, weight=1)

        row = 0
        label = ttk.Label(frame, text="Provider")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.provider,
            state=WidgetState.READONLY,
            takefocus=0,
        )
        entry.grid(row=row, column=1, sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Name")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.name,
        )
        entry.grid(row=row, column=1, sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Model")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.model_name,
        )
        entry.grid(row=row, column=1, sticky=tk.EW, padx=PAD)

        row += 1
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

        row += 1

        label = ttk.Label(frame, text="Output cost")
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.output_cost,
            justify="right",
            width=7,
        )
        entry.grid(row=row, column=1, sticky=tk.W, padx=PAD)
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("save", self._save, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _check_value_changed(self, *args) -> None:
        enable = False
        if self.mode == Mode.NEW:
            if (
                self.name.get()
                and self._safe_get_double(self.input_cost) > 0
                and self._safe_get_double(self.output_cost) > 0
            ):
                enable = True
        else:
            enable = self._record_changes()
        self.button_frame.enable(enable)

    def _safe_get_double(self, var: tk.DoubleVar) -> float:
        """Return the DoubleVar value, or 0.0 if empty/invalid."""
        try:
            return var.get()
        except TclError:
            return 0.0

    def _record_changes(self) -> dict:
        changes = {}
        if self.model.model != self.model_name.get():
            changes["model"] = (
                self.model.model,
                self.model_name.get(),
            )
        if self.model.costs.input != self._safe_get_double(self.input_cost):
            changes["input_cost"] = (
                self.model.costs.input,
                self._safe_get_double(self.input_cost),
            )
        if self.model.costs.output != self._safe_get_double(self.output_cost):
            changes["output_cost"] = (
                self.model.costs.output,
                self._safe_get_double(self.output_cost),
            )
        return changes

    def _save(self, *args) -> None:
        save_model(
            Model(
                name=self.name.get(),
                provider=self.provider.get(),
                model=self.model_name.get(),
                costs=UsageCosts(
                    input=self._safe_get_double(self.input_cost),
                    output=self._safe_get_double(self.output_cost),
                ),
            )
        )
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()

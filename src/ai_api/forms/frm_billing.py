"""BillingFrame for AI Interface."""

import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from psiutils.buttons import ButtonFrame
from psiutils.constants import PAD, Mode
from psiutils.menus import Menu, MenuItem
from psiutils.treeview import sort_treeview
from psiutils.utilities import window_resize

from ai_api.config import read_config
from ai_api.constants import APP_TITLE
from ai_api.forms.frm_model import ModelEditFrame
from ai_api.models import MODELS, delete_model
from ai_api.providers import PROVIDERS
from ai_api.text import Text

txt = Text()

FRAME_TITLE = f"{APP_TITLE} - Billing"
DEFAULT_GEOMETRY = "100x100"
DATETIME_FORMAT = "%d %b %Y at %H:%M"
COST_FORMAT = ".2f"


@dataclass(frozen=True)
class TreeColumn:
    """Definition of a Treeview column."""

    key: str
    heading: str
    width: int
    anchor: str


TREE_COLUMNS = (
    TreeColumn("name", "Name", 200, tk.W),
    TreeColumn("model", "Model", 200, tk.W),
    TreeColumn("input", "Input", 75, tk.E),
    TreeColumn("output", "Output", 75, tk.E),
)


class BillingFrame:
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()
        self.selected_model = None

        # tk variables
        self.provider = tk.StringVar()
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

        self.context_menu = self._context_menu()

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        row = 0
        provider_frame = self._provider_frame(frame)
        provider_frame.grid(row=row, column=0, sticky=tk.EW)

        row += 1
        # details_frame = self._details_frame(frame)
        # details_frame.grid(row=row, column=0, sticky=tk.EW)
        models_frame = self._models_frame(frame)
        models_frame.grid(row=row, column=0, sticky=tk.NSEW)

        return frame

    def _provider_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        row = 0
        for column, provider in enumerate(list(PROVIDERS.keys())):
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

    def _models_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.model_tree = self._model_tree_frame(frame)
        self.model_tree.grid(row=0, column=0, sticky=tk.NSEW)

        return frame

    def _model_tree_frame(self, master: tk.Frame) -> ttk.Treeview:
        """Return  a tree widget."""
        tree = ttk.Treeview(
            master,
            selectmode="browse",
            show="headings",
        )
        tree.bind("<<TreeviewSelect>>", self._tree_clicked)
        tree.bind("<Button-3>", self._show_context_menu)

        tree["columns"] = tuple(col.key for col in TREE_COLUMNS)
        for col in TREE_COLUMNS:
            (col_key, col_text, col_width) = (col.key, col.heading, col.width)
            tree.heading(
                col_key,
                text=col_text,
                command=lambda c=col_key: sort_treeview(tree, c, False),
            )
            tree.column(col_key, width=col_width, anchor=col.anchor)
            tree.column(col.key, stretch=tk.NO)
        tree.column(col.key, stretch=tk.YES)
        return tree

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            # frame.icon_button("build", self._process, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _populate_model_tree(self) -> None:
        self.model_tree.delete(*self.model_tree.get_children())
        for name, model in sorted(MODELS.items()):
            if model.provider != self.provider.get():
                continue
            values = (
                name,
                model.model,
                f"${model.costs.input:{COST_FORMAT}}",
                f"${model.costs.output:{COST_FORMAT}}",
            )
            self.model_tree.insert("", "end", values=values)

    def _tree_clicked(self, *args) -> None:
        self.selected_item = self.model_tree.selection()
        values = self.model_tree.item(self.selected_item)["values"]
        if self.selected_item:
            self.selected_model = MODELS.get(values[0])
            self.context_menu.enable(True)

    def _show_context_menu(self, event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
        selected_item = self.model_tree.identify_row(event.y)
        self.model_tree.selection_set(selected_item)

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem("New ...", self._new_model),
            MenuItem("Edit ...", self._edit_model, dimmable=True),
            MenuItem("Delete ...", self._delete_model, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _update_provider(self) -> None:
        self._populate_model_tree()

    def _save_balance(self, *args) -> None:
        pass

    def _new_model(self, *args) -> None:
        dlg = ModelEditFrame(self, Mode.NEW, provider=self.provider.get())
        self.root.wait_window(dlg.root)
        self._populate_model_tree()

    def _edit_model(self, *args) -> None:
        dlg = ModelEditFrame(
            self,
            Mode.EDIT,
            provider=self.provider.get(),
            model=self.selected_model,
        )
        self.root.wait_window(dlg.root)
        self._populate_model_tree()

    def _delete_model(self, *args) -> None:
        dlg = tk.messagebox.askyesno(
            "Delete Model",
            f"Are you sure you want to delete {self.selected_model.name}?",
        )
        if dlg:
            delete_model(self.selected_model)
            self._populate_model_tree()

    def _dismiss(self, *args) -> None:
        self.root.destroy()

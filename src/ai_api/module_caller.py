"""Module caller for AI Interface."""

from ai_api.forms.frm_billing import BillingFrame
from ai_api.forms.frm_config import ConfigFrame
from ai_api.forms.frm_main import AppFrame


class ModuleCaller:
    """
    Handles the invocation of specific module dialogs in a GUI application.

    Initialized with a root window and the name of a module to call. Maps
    the module name to a corresponding method, invokes it, and manages the
    GUI dialog lifecycle (e.g., waiting for it to close, destroying the root).

    Parameters:
        root (tk.Tk or similar): The root window for the GUI.
        module (str): The name of the module or command to invoke.

    Behaviour:
        - If 'module' is '-h', lists available modules and exits.
        - If 'module' is unrecognized, prints an error and sets `invalid` to
          True.
        - If 'module' is valid, runs the corresponding dialog method.
        - Destroys the root window after handling the module (unless invalid).

    Attributes:
        invalid (bool): Set to True if the module was invalid or help was
        requested.

    Supported Modules:
        - config: Opens the ConfigFrame dialog.
        - main: No action, but included for completeness.
    """

    def __init__(self, root, module) -> None:
        """
        Initialise ModuleCaller to invoke a specified module function.

        If the module argument is '-h', lists all available modules including
        'main' and marks the instance as invalid.

        If the module name is invalid (not recognised or not 'main'),
        marks the instance as invalid.

        Otherwise, calls the requested module method, then destroys the root
        window. The 'main' argument is treated slightly differently.

        Args:
            root: The root Tkinter window or parent widget.
            module: The module name or command to execute.
        """
        modules = {
            "main": self._main,
            "config": self._config,
            "billing": self._billing,
        }

        if module == "-h":
            for key in sorted(list(modules.keys()) + ["main"]):
                print(key)
            self.invalid = True
            return

        if module not in modules and module != "main":
            self.invalid = True
            return

        self.invalid = False
        self.root = root
        modules[module]()
        if module != "main":
            self.root.destroy()
        return

    def _main(self) -> None:
        """
        Open the main frame and wait until it is closed.
        """
        AppFrame(self.root)

    def _config(self) -> None:
        """
        Open the configuration dialog and wait until it is closed.
        """
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _billing(self) -> None:
        """
        Open the billing dialog and wait until it is closed.
        """
        dlg = BillingFrame(self)
        self.root.wait_window(dlg.root)

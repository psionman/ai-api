"""Initialise the application."""
from psiutils.utilities import psi_logger
from ai_api.constants import APP_NAME
from ai_api._version import __version__

version = __version__

logger = psi_logger(APP_NAME)

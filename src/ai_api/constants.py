"""Constants for AI Interface."""

from pathlib import Path

from appdirs import user_config_dir, user_data_dir
from psiutils.known_paths import resolve_path

# General
AUTHOR = "Jeff Watkins"
APP_NAME = "ai_api"  # must be package name i.e. directory under /src/
APP_AUTHOR = "psionman"
HTML_DIR = resolve_path("html", __file__)
HELP_URI = ""
EDITOR = "kate"

# Paths
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), "config.toml")
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
USER_DATA_FILE_NAME = "data.json"
USER_DATA_FILE = Path(USER_DATA_DIR, USER_DATA_FILE_NAME)
HOME = str(Path.home())
USAGE_FILE = "usage.csv"

OUTPUT_DIR = Path(USER_DATA_DIR, "ai_output")
OUTPUT_DIR.mkdir(exist_ok=True)

QUESTION_DIR = Path(USER_DATA_DIR, "ai_input")
QUESTION_DIR.mkdir(exist_ok=True)

# GUI
APP_TITLE = "AI Interface"
ICON_FILE = Path(Path(__file__).parent, "images", "head-cog-outline.png")

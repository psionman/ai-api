"""Read and write user data file."""
import json
from pathlib import Path


from ai_api.constants import USER_DATA_DIR, USER_DATA_FILE
from ai_api import logger

class JsonFile():
    """Utility to retrieve and save a json file."""
    def __init__(self, path: str, content: dict = None):
        self.path = path
        if not content:
            content = {}
        self.content = content

    def read(self):
        """Set the class's content value if file exists."""
        try:
            with open(self.path, 'r', encoding='utf8') as f_json:
                self.content = json.load(f_json)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            logger.error(f'Invalid json in {self.path}.')

    def write(self):
        """Write the class's content value."""
        Path(self.path.parent).mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w', encoding='utf8') as f_json:
            json.dump(self.content, f_json)


class DataFile(JsonFile):
    """Utility to retrieve and save user data file."""
    def __init__(self, content: dict = None):
        path = Path(USER_DATA_DIR, USER_DATA_FILE)
        super().__init__(path, content)

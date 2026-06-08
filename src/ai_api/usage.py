# usage.py

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ai_api.constants import USAGE_FILE, USER_DATA_DIR

PATH = Path(USER_DATA_DIR, USAGE_FILE)
FIELD_NAMES = ["timestamp", "provider", "input_tokens", "output_tokens"]


@dataclass
class UsageCosts:
    input: float
    output: float


CLAUDE_COSTS = UsageCosts(input=0.1, output=0.0015)
OPENAI_COSTS = UsageCosts(input=0.1, output=0.4)


class Usage:
    def __init__(self, input: int = 0, output: int = 0, provider: str = ""):
        self.input_tokens = input
        self.output_tokens = output
        self.provider = provider
        self.timestamp = datetime.now()

    def serialize(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

    def deserialize(self, data: dict):
        self.timestamp = datetime.fromisoformat(data["timestamp"])
        self.provider = data["provider"]
        self.input_tokens = int(data["input_tokens"])
        self.output_tokens = int(data["output_tokens"])

    def save(self):
        self._write_csv_file()

    def _write_csv_file(self):
        write_header = not PATH.exists()
        with open(PATH, "a", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=FIELD_NAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(self.serialize())


def load_usage():
    """Load usage data from the CSV file."""
    if not PATH.exists():
        return []

    usages = []
    with open(PATH, newline="", encoding="utf-8") as f_csv:
        reader = csv.DictReader(f_csv)
        for row in reader:
            usage = Usage()
            usage.deserialize(row)
            usages.append(usage)

    return usages

# providers.py

import json
from datetime import datetime

from ai_api.constants import PROVIDERS_FILE
from ai_api.prompts import (
    AnthropicPrompt,
    OpenAIPrompt,
    Prompt,
)

PROMPT_CLASSES: dict[str, Prompt] = {
    "Anthropic": AnthropicPrompt,
    "Open AI": OpenAIPrompt,
}


class Provider:
    def __init__(
        self, name: str, balance: float = 0.0, last_updated: datetime = None
    ):
        self.name = name
        self.balance = balance
        self.last_updated = last_updated or datetime.now()
        if name in PROMPT_CLASSES:
            self.prompt_class = PROMPT_CLASSES[name]
        else:
            self.prompt_class = None

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "balance": self.balance,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Provider":
        return cls(
            name=data["name"],
            balance=data.get("balance", 0.0),
            last_updated=datetime.fromisoformat(data["last_updated"])
            if "last_updated" in data
            else datetime.now(),
        )


def get_providers() -> dict[str, Provider]:
    with open(PROVIDERS_FILE) as f:
        data = json.load(f)
        providers = {}
        for item in data:
            if item:
                provider = Provider.deserialize(item)
                providers[provider.name] = provider
        return providers


def save_providers(providers: dict[str, Provider]) -> None:
    output = [provider.serialize() for provider in providers.values()]
    with open(PROVIDERS_FILE, "w") as f:
        json.dump(output, f)


PROVIDERS = get_providers()

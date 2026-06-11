# providers.py

import json
from datetime import datetime

from usage import load_usage

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

COSTS_PER = 10**6


class Provider:
    def __init__(
        self, name: str, balance: float = 0.0, last_updated: datetime = None
    ):
        self.name = name
        self.balance = balance
        self.last_updated = last_updated or datetime.now()
        self._usage = 0.0
        self._remaining = 0.0
        if name in PROMPT_CLASSES:
            self.prompt_class = PROMPT_CLASSES[name]
        else:
            self.prompt_class = None
        self.last_usage_calc = datetime(2000, 1, 1)
        self.models: dict[str, object] = {}

    def add_model(self, model: object) -> None:
        self.models[model.name] = model

    @property
    def usage(self) -> float:
        delta = datetime.now() - self.last_usage_calc
        seconds = int(delta.total_seconds())
        if seconds < 5:
            return self._usage
        self._usage = self._get_usage()
        self.last_usage_calc = datetime.now()
        return self._usage

    @property
    def remaining(self) -> float:
        self._remaining = self.balance - self.usage
        return self._remaining

    def _get_usage(self) -> float:
        usage = 0
        data = load_usage()
        for usage_item in data:
            if (
                usage_item
                and usage_item.provider == self.name
                and usage_item.timestamp > self.last_updated
            ):
                model = self.models.get(usage_item.model, None)
                if not model:
                    continue
                input_usage = usage_item.input_tokens * model.costs.input
                output_usage = usage_item.output_tokens * model.costs.output
                usage += (input_usage + output_usage) / COSTS_PER
        return usage

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
            balance=float(data.get("balance", 0.0)),
            last_updated=datetime.fromisoformat(data["last_updated"])
            if "last_updated" in data
            else datetime.now(),
        )


def save_provider(provider: Provider) -> None:
    PROVIDERS[provider.name] = provider
    save_providers(PROVIDERS)


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

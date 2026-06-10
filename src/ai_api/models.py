# models.py

import json
from dataclasses import dataclass

from ai_api.constants import USER_DATA_FILE
from ai_api.prompts import (
    AnthropicPrompt,
    OpenAIPrompt,
    Prompt,
)

PROMPT_CLASSES: dict[str, Prompt] = {
    "anthropic": AnthropicPrompt,
    "openai": OpenAIPrompt,
}


@dataclass
class UsageCosts:
    input: float
    output: float

    def serialize(self) -> dict[str, float]:
        return {
            "input": self.input,
            "output": self.output,
        }

    @classmethod
    def deserialize(cls, data: dict[str, float]) -> "UsageCosts":
        return cls(
            input=data["input"],
            output=data["output"],
        )


class Model:
    def __init__(
        self,
        name: str,
        provider: str,
        model: str,
        costs: UsageCosts,
        handler: str,
    ):
        self.name = name
        self.provider = provider
        self.model = model
        self.costs = costs
        self.handler = handler
        self.prompt_class = PROMPT_CLASSES[handler](
            model,
        )
        print(self.prompt_class)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "model": self.model,
            "provider": self.provider,
            "costs": self.costs.serialize(),
            "handler": self.handler,
        }

    @classmethod
    def deserialize(cls, data: dict[str, float]) -> "Model":
        return cls(
            name=data["name"],
            model=data["model"],
            provider=data["provider"],
            costs=UsageCosts.deserialize(data["costs"]),
            handler=data["handler"],
        )


def get_models() -> list[Model]:
    with open(USER_DATA_FILE) as f:
        data = json.load(f)
        models = {}
        for item in data:
            if item:
                model = Model.deserialize(item)
                models[model.name] = model
        return models


def save_models(models: list[Model]) -> None:
    output = [model.serialize() for model in models]
    with open(USER_DATA_FILE, "w") as f:
        json.dump(output, f)


MODELS = get_models()

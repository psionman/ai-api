# models.py

import json
from dataclasses import dataclass

from ai_api.constants import MODELS_FILE
from ai_api.providers import PROVIDERS


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
    ):
        self.name = name
        self.provider = provider
        self.model = model
        self.costs = costs
        self.prompt_class = PROVIDERS[provider].prompt_class(name)

    def __repr__(self) -> str:
        return f"Model(name='{self.name}', provider='{self.provider}', model='{self.model}', costs={self.costs})"

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "model": self.model,
            "provider": self.provider,
            "costs": self.costs.serialize(),
        }

    @classmethod
    def deserialize(cls, data: dict[str, float]) -> "Model":
        return cls(
            name=data["name"],
            model=data["model"],
            provider=data["provider"],
            costs=UsageCosts.deserialize(data["costs"]),
        )


def get_models() -> list[Model]:
    with open(MODELS_FILE) as f:
        data = json.load(f)
        models = {}
        for item in data:
            if item:
                model = Model.deserialize(item)
                models[model.name] = model
                provider = PROVIDERS.get(model.provider)
                if provider:
                    provider.add_model(model)
        return models


def delete_model(model: Model) -> None:
    del MODELS[model.name]
    save_models(list(MODELS.values()))


def save_model(model: Model) -> None:
    MODELS[model.name] = model
    save_models(list(MODELS.values()))


def save_models(models: list[Model]) -> None:
    output = [model.serialize() for model in models]
    with open(MODELS_FILE, "w") as f:
        json.dump(output, f)


MODELS = get_models()

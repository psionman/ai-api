# providers.py

from dataclasses import dataclass


@dataclass
class UsageCosts:
    input: float
    output: float


class Provider:
    def __init__(self, name: str, model: str, costs: UsageCosts):
        self.name = name
        self.model = model
        self.costs = costs


providers = {
    "Claude Opus-4-6": Provider(
        "claude", "claude-opus-4-6", UsageCosts(input=3, output=15)
    ),
    "GPT-4o": Provider("openai", "gpt-4o", UsageCosts(input=2.5, output=15)),
}

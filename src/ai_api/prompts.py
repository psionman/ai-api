# openai.py

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

from ai_api.usage import Usage

load_dotenv()  # loads OPENAI_API_KEY and ANTHROPIC_API_KEY


class Prompt:
    def __init__(self, model: str):
        self.model = model
        self.provider = ""
        self._client = None
        self._system = ""
        self._prompt = ""

    def __repr__(self) -> str:
        return f"Prompt(model='{self.model}')"

    def send(self) -> str:
        return self._send_prompt()

    @property
    def client(self) -> object:
        return self._client

    @client.setter
    def client(self, value: object) -> None:
        self._client = value

    @property
    def system(self) -> str:
        return self._system

    @system.setter
    def system(self, value: str) -> None:
        self._system = value

    @property
    def prompt(self) -> str:
        return self._prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self._prompt = value

    def _save_usage(self, input_usage: int, output_usage: int) -> None:
        usage_record = Usage(
            input=input_usage,
            output=output_usage,
            provider=self.provider,
            model=self.model,
        )
        usage_record.save()


class OpenAIPrompt(Prompt):
    def __init__(self, model: str):
        super().__init__(model)
        self.client = OpenAI()
        self.provider = "Open AI"

    def send(self) -> str:
        """Send a prompt to OpenAI and return the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system},
                    {"role": "user", "content": self.prompt},
                ],
            )
        except self.client._exceptions.RateLimitError as e:
            if "insufficient_quota" in str(e):
                raise RuntimeError(
                    "OpenAI quota exceeded. Please top up your account."
                ) from e
            raise

        usage = response.usage
        self._save_usage(usage.prompt_tokens, usage.completion_tokens)
        return response.choices[0].message.content


class AnthropicPrompt(Prompt):
    def __init__(self, model: str):
        super().__init__(model)
        self.client = Anthropic()
        self.provider = "Anthropic"

    def send(self) -> str:
        """Send a prompt to Anthropic and return the response."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system,
                messages=[{"role": "user", "content": self.prompt}],
            )
        except self.client._exceptions.RateLimitError as e:
            raise RuntimeError(
                "Anthropic quota exceeded. Please check your account."
            ) from e

        usage = message.usage
        self._save_usage(usage.input_tokens, usage.output_tokens)
        return message.content[0].text

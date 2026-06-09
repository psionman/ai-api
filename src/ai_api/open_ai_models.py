# openai.py

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

from ai_api.usage import Usage

load_dotenv()

client = OpenAI()  # reads OPENAI_API_KEY env var


def open_ai_prompt(
    system: str,
    prompt: str,
    model: str = "gpt-4o",
) -> str:
    try:
        return _send_prompt(system, prompt, model)
    except RateLimitError as e:
        if "insufficient_quota" in str(e):
            # Show user-friendly message
            raise RuntimeError(
                "OpenAI quota exceeded. Please top up your account."
            ) from e
        raise


def _send_prompt(system: str, prompt: str, model: str = "gpt-4o") -> str:
    """Send a prompt to ChatGPT and return the response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    usage = response.usage
    usage_record = Usage(
        input=usage.prompt_tokens,
        output=usage.completion_tokens,
        provider=response.model,
    )
    usage_record.save()
    return response.choices[0].message.content

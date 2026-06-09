# claude.py

import anthropic
from dotenv import load_dotenv

from ai_api.usage import Usage

load_dotenv()

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var


def anthropic_prompt(system: str, prompt: str) -> str:
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    usage = message.usage

    usage_record = Usage(
        input=usage.input_tokens,
        output=usage.output_tokens,
        provider=message.model,
    )
    usage_record.save()

    return message.content[0].text

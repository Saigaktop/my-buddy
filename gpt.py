import os
from openai import AsyncOpenAI
from prompts import SYSTEM_PROMPT

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# OpenAI model can be set via environment variable
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

async def ask_gpt(text: str) -> str:
    """Send text to the configured OpenAI model and return the response."""
    chat = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return chat.choices[0].message.content

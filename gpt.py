import os
from openai import AsyncOpenAI
from prompts import SYSTEM_PROMPT

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_gpt(text: str) -> str:
    """Send text to OpenAI GPT-4.1 and return the response."""
    chat = await client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return chat.choices[0].message.content

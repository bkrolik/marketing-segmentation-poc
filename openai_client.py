import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI


# Load the right env file depending on environment
if os.getenv("ENV") == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv()

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def llm(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = await asyncio.wait_for(
                _get_client().responses.create(
                    model="gpt-5-mini",
                    input=prompt,
                    max_output_tokens=300,
                    temperature=0.2,
                ),
                timeout=10,
            )
            return response.output_text
        except Exception as e:
            if attempt == 2:
                raise e
            await asyncio.sleep(0.5 * (attempt + 1))

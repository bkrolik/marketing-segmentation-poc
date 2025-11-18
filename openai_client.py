"""
Async helper for calling the OpenAI Responses API with retry logic.

Loads environment variables and exposes an `llm` coroutine that returns
the response text for a given prompt.
"""

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
    """
    Create or return a cached AsyncOpenAI client.

    Raises:
        RuntimeError: If `OPENAI_API_KEY` is not set in the environment.

    Returns:
        AsyncOpenAI: Configured async OpenAI client instance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def llm(prompt: str) -> str | None:
    """
    Call the OpenAI Responses API asynchronously with basic retry/backoff.

    Args:
        prompt (str): Text prompt to send to the model.

    Returns:
        str: The text output from the model.

    Raises:
        Exception: Propagates the last exception raised after retrying.
    """

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

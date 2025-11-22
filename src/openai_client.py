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


load_dotenv(os.getenv("ENV_FILE", ".env"))

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


async def llm(prompt: str) -> str:
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
                raise RuntimeError(f"Failed to get a response from the LLM after {attempt+1} attempts: {e}")
            await asyncio.sleep(0.5 * (attempt + 1))
    # The function is declared to return `str` — ensure no code path falls through
    # and implicitly returns `None`. If we reach this point the retry loop completed
    # without returning a response (which should not normally happen because the
    # last attempt raises). Raise a clear, explicit error so callers receive a
    # well-defined exception rather than `None`.
    raise RuntimeError("Failed to get a response from the LLM after retries")

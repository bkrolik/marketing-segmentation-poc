import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

# Load the right env file depending on environment
if os.getenv("ENV") == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def llm(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = await asyncio.wait_for(
                client.responses.create(
                    model="gpt-5-mini",
                    input=prompt,
                    max_output_tokens=300,
                    temperature=0.2
                ),
                timeout=10)
            return response.output_text
        except Exception as e:
            if attempt == 2:
                raise e
            await asyncio.sleep(0.5 * (attempt + 1))
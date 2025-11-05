import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load the right env file depending on environment
if os.getenv("ENV") == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def llm(prompt: str) -> str:
    response = await client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return response.output_text
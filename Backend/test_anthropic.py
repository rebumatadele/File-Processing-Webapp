# test_anthropic_provider.py

import asyncio
from app.providers.anthropic_provider import generate_with_anthropic
import os

async def test_anthropic():
    prompt = "Tell me a story about a brave knight."
    api_key = os.getenv("ANTHROPIC_API_KEY")  # Ensure this is set correctly in your environment

    try:
        response = await generate_with_anthropic(prompt, api_key)
        print("Anthropic Response:", response)
    except Exception as e:
        print(f"Failed to generate response from Anthropic: {e}")

if __name__ == "__main__":
    asyncio.run(test_anthropic())

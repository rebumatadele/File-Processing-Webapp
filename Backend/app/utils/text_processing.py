# app/utils/text_processing.py

from typing import List, Generator
from nltk import sent_tokenize
from app.utils.file_utils import handle_error
from app.providers.openai_provider import generate_with_openai
from app.providers.anthropic_provider import generate_with_anthropic
from app.providers.gemini_provider import generate_with_gemini

def split_text_into_chunks(text: str, chunk_size: int, chunk_by: str = "words") -> Generator[str, None, None]:
    if chunk_by == "words":
        words = text.split()
        for i in range(0, len(words), chunk_size):
            yield ' '.join(words[i:i + chunk_size])
    elif chunk_by == "sentences":
        sentences = sent_tokenize(text)
        for i in range(0, len(sentences), chunk_size):
            yield ' '.join(sentences[i:i + chunk_size])
    elif chunk_by == "paragraphs":
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            yield paragraph
    else:
        handle_error("InvalidInput", f"Invalid chunk_by value: {chunk_by}")
        raise ValueError(f"Invalid chunk_by value: {chunk_by}")

async def process_text_stream(
    text: str,
    provider_choice: str,
    prompt: str,
    chunk_size: int = 500,
    chunk_by: str = "words",
    model_choice: str = None,
    api_keys: dict = None
) -> List[str]:
    """
    Processes text by splitting into chunks and generating responses.
    Returns a list of responses.
    """
    final_response = []
    try:
        for chunk in split_text_into_chunks(text, chunk_size, chunk_by):
            try:
                if provider_choice == "OpenAI":
                    response = await generate_with_openai(prompt + chunk, model=model_choice)
                elif provider_choice == "Anthropic":
                    response = await generate_with_anthropic(prompt + chunk, api_key=api_keys.get("ANTHROPIC_API_KEY", ""))
                elif provider_choice == "Gemini":
                    response = await generate_with_gemini(prompt + chunk, model=model_choice)
                else:
                    handle_error("InvalidInput", f"Unsupported provider: {provider_choice}")
                    response = "[Unsupported provider.]"
            except Exception as e:
                handle_error("ProcessingError", str(e))
                response = "[Failed to process this chunk.]"
            final_response.append(response)
    except Exception as e:
        handle_error("ProcessingError", f"Stream processing failed: {e}")
        final_response.append("[Processing failed due to an unexpected error.]")
    return final_response

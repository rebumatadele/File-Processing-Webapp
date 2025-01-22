# config/api_config.py

import openai
import google.generativeai as genai
from anthropic import Anthropic
from app.providers.anthropic_provider import validate_anthropic_api_key

def configure_openai(api_key):
    openai.api_key = api_key
    # (Optional) If you want to also verify OpenAI key:
    # you could do a small test call to openai.Model.list() etc.

def configure_anthropic(api_key):
    try:
        # Check if the key is valid
        valid = validate_anthropic_api_key(api_key)
        if not valid:
            raise Exception("Invalid Anthropic API key")

        # If valid, create the Anthropic instance
        anthropic_instance = Anthropic(api_key=api_key)
        return anthropic_instance

    except Exception as e:
        raise Exception(f"Failed to configure Anthropic: {e}")

def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        # (Optional) do a test call if you want to confirm validity
    except Exception as e:
        raise Exception(f"Failed to configure Gemini: {e}")

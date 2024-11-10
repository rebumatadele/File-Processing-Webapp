# config/load_env.py

from dotenv import load_dotenv
import os

def load_environment_variables():
    load_dotenv()  # Load environment variables from .env file or system
    required_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_FROM",
        "MAIL_PORT",
        "MAIL_SERVER",
        # Add other required variables as needed
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
        "MAIL_FROM": os.getenv("MAIL_FROM"),
        "MAIL_PORT": int(os.getenv("MAIL_PORT")),
        "MAIL_SERVER": os.getenv("MAIL_SERVER"),
        "MAIL_TLS": os.getenv("MAIL_TLS", "True") == "True",
        "MAIL_SSL": os.getenv("MAIL_SSL", "False") == "True",
    }
    return env_vars

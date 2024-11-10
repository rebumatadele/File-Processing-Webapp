# app/utils/environment.py

import os
from dotenv import load_dotenv
from app.utils.file_utils import handle_error
import sys

def load_environment_variables():
    """
    Loads environment variables from a .env file.
    """
    try:
        load_dotenv()  # Automatically loads .env from the current directory
        print("Environment variables loaded successfully.")
    except Exception as e:
        handle_error("EnvironmentError", f"Failed to load environment variables: {e}")
        sys.exit(1)  # Exit the application if env vars cannot be loaded

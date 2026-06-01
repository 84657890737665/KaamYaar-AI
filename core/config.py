"""
core/config.py

Loads and validates environment variables for the entire project.
Any agent or utility that needs configuration should import from here.
"""

import os
from dotenv import load_dotenv

# Load variables from the .env file in the project root
load_dotenv()


def get_gemini_api_key() -> str:
    """
    Returns the Gemini API key from environment variables.
    Raises a clear error if the key is not set.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Please copy .env.example to .env and fill in your API key."
        )
    return key

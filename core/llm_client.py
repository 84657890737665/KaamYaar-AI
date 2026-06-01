"""
core/llm_client.py

Provides a centralised, cached Gemini client factory.
All agents should obtain their client via get_gemini_client() so that
configuration and initialisation logic lives in one place.
"""

import google.genai as genai
from core.config import get_gemini_api_key

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    """
    Returns a shared, lazily-initialised Gemini client.
    The client is created once and reused across all agents.
    """
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_gemini_api_key())
    return _client

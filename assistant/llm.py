"""Create an OpenAI-compatible client for Ollama, OpenAI, or Groq."""

import os
from types import SimpleNamespace

from openai import OpenAI

from assistant.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def get_model() -> str:
    if LLM_PROVIDER == "openai":
        return OPENAI_MODEL
    if LLM_PROVIDER == "groq":
        return GROQ_MODEL
    return OLLAMA_MODEL


def create_client() -> OpenAI:
    # Development: allow a `mock` provider for fast local responses
    if os.getenv("LLM_PROVIDER", "").lower() == "mock":
        class _MockCompletions:
            def create(self, model=None, messages=None, tools=None, tool_choice=None):
                class _Msg:
                    def __init__(self, content):
                        self.content = content
                        self.tool_calls = []

                class _Choice:
                    def __init__(self, msg):
                        self.message = msg

                resp = SimpleNamespace(choices=[_Choice(_Msg("(mock) " + (messages[-1]["content"] if messages else "ok")))])
                return resp

        mock_client = SimpleNamespace()
        mock_client.chat = SimpleNamespace(completions=_MockCompletions())
        return mock_client

    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not set in .env"
            )
        return OpenAI(api_key=OPENAI_API_KEY)

    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com"
            )
        return OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    # Default: Ollama (local, no API key needed)
    return OpenAI(
        api_key="ollama",
        base_url=OLLAMA_BASE_URL,
    )


def provider_info() -> str:
    model = get_model()
    if LLM_PROVIDER == "ollama":
        return f"Ollama ({model}) at {OLLAMA_BASE_URL}"
    return f"{LLM_PROVIDER} ({model})"

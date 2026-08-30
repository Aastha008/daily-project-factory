"""
LLM Provider Factory to instantiate the requested or auto-detected provider.
"""

from __future__ import annotations

import os
from typing import Optional
from factory.config import settings
from factory.llm.base import LLMProvider
from factory.llm.mock_provider import MockLLMProvider


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    force_mock: bool = False,
) -> LLMProvider:
    """
    Resolve and instantiate an LLM provider.
    Fallback priority: Explicit param -> Env Var -> Settings -> Mock.
    """
    if force_mock or settings.mock_llm:
        return MockLLMProvider(model_name=model_name or "mock-model")

    prov = (provider_name or settings.llm_provider).lower()
    model = model_name or settings.model_name

    # Gemini
    if prov in ["gemini", "google"]:
        key = api_key or settings.gemini_api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            # If no key available, fallback to mock provider gracefully with a notice
            return MockLLMProvider(model_name=model)
        from factory.llm.gemini_provider import GeminiProvider
        return GeminiProvider(model_name=model, api_key=key)

    # OpenAI
    elif prov in ["openai", "chatgpt"]:
        key = api_key or settings.openai_api_key
        if not key:
            return MockLLMProvider(model_name=model)
        from factory.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(model_name=model, api_key=key)

    # Groq
    elif prov in ["groq"]:
        key = api_key or settings.groq_api_key
        if not key:
            return MockLLMProvider(model_name=model)
        from factory.llm.groq_provider import GroqProvider
        return GroqProvider(model_name=model, api_key=key)

    # Mock
    elif prov in ["mock", "test", "offline"]:
        return MockLLMProvider(model_name=model)

    # Default auto-detect
    if settings.gemini_api_key:
        from factory.llm.gemini_provider import GeminiProvider
        return GeminiProvider(model_name=model, api_key=settings.gemini_api_key)
    elif settings.openai_api_key:
        from factory.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(model_name=model, api_key=settings.openai_api_key)
    elif settings.groq_api_key:
        from factory.llm.groq_provider import GroqProvider
        return GroqProvider(model_name=model, api_key=settings.groq_api_key)

    return MockLLMProvider(model_name=model)

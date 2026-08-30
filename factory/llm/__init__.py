"""
LLM abstraction layer supporting multiple providers with unified JSON parsing.
"""

from factory.llm.base import LLMProvider
from factory.llm.factory import get_llm_provider

__all__ = ["LLMProvider", "get_llm_provider"]

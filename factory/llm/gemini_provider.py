"""
Google Gemini LLM Provider implementation with multi-model fallback.
"""

from __future__ import annotations

import os
from typing import Optional
from factory.llm.base import LLMProvider
from factory.utils.logger import factory_logger


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider implementation with automatic model fallback."""

    FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def __init__(self, model_name: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        super().__init__(model_name=model_name or "gemini-2.0-flash", api_key=key)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided for GeminiProvider")

        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=self.api_key)
        self.types = types

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for model in models_to_try:
            try:
                config_kwargs = {}
                if system_prompt:
                    config_kwargs["system_instruction"] = system_prompt
                if temperature is not None:
                    config_kwargs["temperature"] = temperature
                if max_tokens:
                    config_kwargs["max_output_tokens"] = max_tokens

                config = self.types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""
            except Exception as exc:
                last_error = exc
                factory_logger.warning(f"Gemini generation with {model} failed: {exc}. Trying next model...")

        factory_logger.error(f"All Gemini models failed: {last_error}. Falling back to deterministic generator.")
        from factory.llm.mock_provider import MockLLMProvider
        mock = MockLLMProvider()
        return mock.generate_text(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

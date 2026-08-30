"""
Google Gemini LLM Provider implementation with dynamic model discovery.
"""

from __future__ import annotations

import os
from typing import List, Optional
from factory.llm.base import LLMProvider
from factory.utils.logger import factory_logger


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider with dynamic active model discovery."""

    DEFAULT_CANDIDATES = [
        "gemini-2.5-flash",
        "gemini-3.6-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        super().__init__(model_name=model_name or "gemini-2.5-flash", api_key=key)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided for GeminiProvider")

        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=self.api_key)
        self.types = types
        self._available_models: List[str] = []
        self._discover_models()

    def _discover_models(self) -> None:
        """Query Gemini API to list all active supported models for this key."""
        try:
            models_page = self.client.models.list()
            active = []
            for m in models_page:
                name = m.name or ""
                # Strip models/ prefix
                clean_name = name.replace("models/", "")
                if "gemini" in clean_name.lower():
                    active.append(clean_name)
            if active:
                self._available_models = active
                factory_logger.info(f"Discovered {len(active)} Gemini models: {active[:4]}")
        except Exception as exc:
            factory_logger.warning(f"Could not list available Gemini models dynamically: {exc}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        # Build prioritized list of models
        models_to_try: List[str] = []
        if self.model_name:
            models_to_try.append(self.model_name)
        for m in self._available_models:
            if m not in models_to_try:
                models_to_try.append(m)
        for m in self.DEFAULT_CANDIDATES:
            if m not in models_to_try:
                models_to_try.append(m)

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
                if response.text:
                    return response.text
            except Exception as exc:
                last_error = exc
                factory_logger.warning(f"Gemini generation with '{model}' failed: {exc}. Trying next candidate...")

        factory_logger.error(f"All Gemini models failed: {last_error}. Using deterministic generator.")
        from factory.llm.mock_provider import MockLLMProvider
        mock = MockLLMProvider()
        return mock.generate_text(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

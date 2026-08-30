"""
Google Gemini LLM Provider implementation with strict text-only model filtering.
"""

from __future__ import annotations

import os
from typing import List, Optional
from factory.llm.base import LLMProvider
from factory.utils.logger import factory_logger


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider with text-only active model filtering."""

    # Prioritized list of active text generation models (no TTS/audio models)
    PRIMARY_MODELS = [
        "gemini-3.6-flash",
        "gemini-3.1-pro-preview",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
    ]

    def __init__(self, model_name: str = "gemini-3.6-flash", api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        super().__init__(model_name=model_name or "gemini-3.6-flash", api_key=key)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided for GeminiProvider")

        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=self.api_key)
        self.types = types
        self._available_models: List[str] = []
        self._discover_models()

    def _discover_models(self) -> None:
        """Query Gemini API to list all active supported TEXT models for this key."""
        try:
            models_page = self.client.models.list()
            active = []
            for m in models_page:
                name = m.name or ""
                clean_name = name.replace("models/", "").strip()
                clean_lower = clean_name.lower()

                # Filter out non-text models (TTS, embedding, audio, imagen, etc.)
                if any(x in clean_lower for x in ["tts", "embedding", "audio", "imagen", "vision-preview"]):
                    continue

                if "gemini" in clean_lower:
                    active.append(clean_name)

            if active:
                self._available_models = active
                factory_logger.info(f"Discovered {len(active)} active text Gemini models: {active[:3]}")
        except Exception as exc:
            factory_logger.warning(f"Could not list available Gemini models dynamically: {exc}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        # Build prioritized list of text models
        models_to_try: List[str] = []
        if self.model_name and not any(x in self.model_name.lower() for x in ["tts", "embedding", "audio"]):
            models_to_try.append(self.model_name)
        for m in self.PRIMARY_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)
        for m in self._available_models:
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
                if response.text and response.text.strip():
                    return response.text.strip()
            except Exception as exc:
                last_error = exc
                err_str = str(exc)
                if "404" in err_str or "NOT_FOUND" in err_str:
                    factory_logger.warning(f"Gemini model '{model}' not found. Trying next candidate...")
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
                    factory_logger.warning(f"Gemini model '{model}' rate-limited. Trying next candidate...")
                else:
                    factory_logger.warning(f"Gemini generation with '{model}' error: {exc}. Trying next candidate...")

        factory_logger.error(f"All Gemini models failed or rate-limited ({last_error}). Using deterministic fallback generator.")
        from factory.llm.mock_provider import MockLLMProvider
        mock = MockLLMProvider()
        return mock.generate_text(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

"""
Google Gemini LLM Provider implementation.
"""

from __future__ import annotations

import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from factory.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider implementation."""

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        super().__init__(model_name=model_name, api_key=key)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided for GeminiProvider")

        # Initialize Google GenAI client
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self._use_new_sdk = True
        except ImportError:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=self.api_key)
            self.client = genai_legacy.GenerativeModel(self.model_name)
            self._use_new_sdk = False

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=2, max=10),
    )
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        if self._use_new_sdk:
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens:
                config["max_output_tokens"] = max_tokens

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config if config else None,
            )
            return response.text or ""
        else:
            generation_config = {"temperature": temperature}
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config,
            )
            return response.text or ""

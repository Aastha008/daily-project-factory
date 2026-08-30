"""
OpenAI LLM Provider implementation.
"""

from __future__ import annotations

import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from factory.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI API Provider implementation."""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(model_name=model_name, api_key=key)
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided for OpenAIProvider")

        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

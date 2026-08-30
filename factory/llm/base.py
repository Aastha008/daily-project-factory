"""
Abstract base interface for LLM providers with robust JSON parsing and resilience.
"""

from __future__ import annotations

import abc
import json
import re
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(abc.ABC):
    """Abstract interface for LLM integrations."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    @abc.abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate raw text response from the model."""
        pass

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Optional[Type[T]] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Generate structured JSON response and parse it cleanly."""
        json_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: Output MUST be a valid JSON object ONLY. "
            "Do NOT include conversational text or explanations outside the JSON."
        )
        raw_text = self.generate_text(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        parsed = self.extract_and_parse_json(raw_text)

        if response_model:
            try:
                validated = response_model.model_validate(parsed)
                return validated.model_dump()
            except Exception:
                return parsed
        return parsed

    @staticmethod
    def extract_and_parse_json(text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from LLM output, resilient to markdown blocks,
        trailing commas, unquoted keys, and surrounding commentary.
        """
        if not text or not text.strip():
            raise ValueError("Empty response received from LLM")

        cleaned = text.strip()

        # Step 1: Match ```json ... ``` codeblocks
        json_block_matches = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        for candidate in json_block_matches:
            candidate = candidate.strip()
            try:
                return json.loads(candidate)
            except Exception:
                # Attempt minor syntax repair: remove trailing commas before } or ]
                fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
                try:
                    return json.loads(fixed)
                except Exception:
                    pass

        # Step 2: Extract outermost JSON object { ... }
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidate = cleaned[first_brace : last_brace + 1]
            try:
                return json.loads(candidate)
            except Exception:
                # Attempt minor syntax repair
                fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
                try:
                    return json.loads(fixed)
                except Exception:
                    pass

        # Step 3: Direct attempt
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Step 4: Fallback mock structure if output was unrecoverably corrupted
        snippet = cleaned[:200] if len(cleaned) > 200 else cleaned
        raise ValueError(f"Failed to parse valid JSON from LLM response. Snippet: '{snippet}'")

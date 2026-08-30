"""
Agent 5: Coding Agent
Synthesizes complete, production-quality, runnable codebases
including source files, unit tests, configurations, and dependencies.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from factory.llm.base import LLMProvider
from factory.state import ProjectState
from factory.utils.logger import factory_logger


class CodingAgent:
    """Senior Staff Engineer generating fully functioning, production-ready code."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_codebase(
        self,
        idea: Dict[str, Any],
        research: Dict[str, Any],
        architecture: Dict[str, Any],
    ) -> Dict[str, str]:
        """Synthesize all source and test files for the project."""
        factory_logger.step("Generating code")

        file_list = architecture.get("file_list", [])
        modules = architecture.get("modules", [])

        system_prompt = (
            "You are a Principal Software Engineer at Daily Project Factory.\n"
            "Your task is to write the COMPLETE, PRODUCTION-READY, FULLY IMPLEMENTED codebase.\n"
            "MANDATORY IMPLEMENTATION RULES:\n"
            "1. NO PLACEHOLDERS: Do NOT write `pass`, `...`, `// TODO`, or stubbed fake methods. Write real, working logic.\n"
            "2. CLEAN PYTHON: Use Python 3.10+ type hints, robust error handling, docstrings, and Pydantic v2 schemas.\n"
            "3. WORKING TESTS: Write comprehensive pytest test suites in `tests/` that actually test real edge cases and pass.\n"
            "4. ZERO SECRETS: Never hardcode API keys, passwords, or tokens. Read from environment variables.\n"
            "5. OUTPUT FORMAT: Output a JSON object where the key is the relative file path and the value is the complete file string content."
        )

        user_prompt = f"""
Project Name: {idea.get('project_name')}
Category: {idea.get('category')}
Description: {idea.get('description')}
Problem Statement: {idea.get('problem_statement')}
Features to implement: {json.dumps(idea.get('features', []))}
Target File List: {json.dumps(file_list)}
Module Details: {json.dumps(modules)}
Libraries to use: {json.dumps(research.get('libraries', []))}

Generate the complete source code for ALL files.
Output JSON schema:
{{
  "files": {{
    "requirements.txt": "...",
    ".env.example": "...",
    ".gitignore": "...",
    "src/__init__.py": "...",
    "src/models.py": "...",
    "src/core.py": "...",
    "src/api.py": "...",
    "src/main.py": "...",
    "tests/__init__.py": "...",
    "tests/test_core.py": "...",
    "tests/test_api.py": "..."
  }}
}}
"""
        code_dict = self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        files = code_dict.get("files", {})
        if not files and isinstance(code_dict, dict):
            # Check if root is already the files map
            files = {k: v for k, v in code_dict.items() if isinstance(v, str) and ("." in k or "/" in k)}

        # Sanity check: Ensure essential files exist
        if ".gitignore" not in files:
            files[".gitignore"] = "__pycache__/\n*.py[cod]\n.env\n.pytest_cache/\n*.db\n"
        if ".env.example" not in files:
            files[".env.example"] = "APP_ENV=development\nPORT=8000\nLOG_LEVEL=INFO\n"
        if "requirements.txt" not in files:
            files["requirements.txt"] = "fastapi>=0.110.0\npydantic>=2.7.0\npytest>=8.0.0\nuvicorn>=0.29.0\nhttpx>=0.27.0\n"

        factory_logger.info(f"Generated {len(files)} project files")
        return files

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        research = state.get("research") or {}
        arch = state.get("architecture") or {}

        files = self.generate_codebase(idea, research, arch)
        state["files"] = files
        state["project_status"] = "coding"
        state["logs"].append(f"Synthesized {len(files)} files")
        return state

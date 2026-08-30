"""
Agent 4: Architecture Agent
Designs complete directory structure, module interfaces, API contracts,
database schemas, data flow pipelines, and configuration specifications.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from factory.llm.base import LLMProvider
from factory.state import ArchitectureData, ProjectState
from factory.utils.logger import factory_logger


class ArchitectureAgent:
    """System Architect structuring modules, contracts, and file boundaries."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def design(self, idea_data: Dict[str, Any], research_data: Dict[str, Any]) -> ArchitectureData:
        """Design modular architecture for the software project."""
        factory_logger.step("Designing architecture")

        system_prompt = (
            "You are the Chief Software Architect at Daily Project Factory.\n"
            "Your job is to design a clean, maintainable, modular architecture for the software project.\n"
            "GUIDELINES:\n"
            "1. Structure code cleanly: `src/` for source code, `tests/` for automated tests.\n"
            "2. Define explicit files: `src/models.py`, `src/core.py`, `src/api.py` or `src/cli.py`, `src/main.py`.\n"
            "3. Ensure the project includes requirements.txt, .env.example, .gitignore, and tests/test_*.py.\n"
            "4. Output MUST be a valid JSON object matching the requested schema."
        )

        user_prompt = f"""
Project Name: {idea_data.get('project_name')}
Category: {idea_data.get('category')}
Description: {idea_data.get('description')}
Features: {json.dumps(idea_data.get('features', []))}
Research Summary: {research_data.get('architecture_overview', '')}
Libraries: {json.dumps(research_data.get('libraries', []))}

Generate the complete architecture specification as JSON:
{{
  "folder_structure": {{
    "src": ["__init__.py", "models.py", "core.py", "api.py", "main.py"],
    "tests": ["__init__.py", "test_core.py", "test_api.py"],
    "root": ["README.md", "requirements.txt", ".env.example", ".gitignore"]
  }},
  "file_list": [
    "src/__init__.py",
    "src/models.py",
    "src/core.py",
    "src/api.py",
    "src/main.py",
    "tests/__init__.py",
    "tests/test_core.py",
    "tests/test_api.py",
    "requirements.txt",
    ".env.example",
    ".gitignore"
  ],
  "modules": [
    {{"name": "src/models.py", "purpose": "Pydantic domain schemas and request/response models"}},
    {{"name": "src/core.py", "purpose": "Core business logic and algorithmic processing engine"}},
    {{"name": "src/api.py", "purpose": "FastAPI HTTP routes, error handlers, and endpoints"}},
    {{"name": "src/main.py", "purpose": "CLI interface and application server entrypoint"}}
  ],
  "apis": [
    {{"endpoint": "/health", "method": "GET", "description": "Service health check"}},
    {{"endpoint": "/api/v1/process", "method": "POST", "description": "Core processing endpoint"}}
  ],
  "database_schema": "SQLite schema if database persistence is needed, otherwise None",
  "data_flow": "Client request -> Pydantic Validation -> Engine Execution -> Structured Result -> Response",
  "env_variables": ["APP_ENV", "PORT", "LOG_LEVEL"],
  "testing_structure": "Pytest test cases in tests/ testing unit methods and API endpoints"
}}
"""
        arch_dict = self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )
        architecture = ArchitectureData.model_validate(arch_dict)
        return architecture

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        research = state.get("research") or {}
        arch = self.design(idea, research)
        state["architecture"] = arch.model_dump()
        state["project_status"] = "architecting"
        state["logs"].append(f"Designed architecture with {len(arch.file_list)} target files")
        return state

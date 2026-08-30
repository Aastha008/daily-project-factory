"""
Agent 3: Project Research Agent
Evaluates technical feasibility, minimal technology requirements,
potential implementation bottlenecks, and security considerations.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from factory.llm.base import LLMProvider
from factory.state import ProjectState, ResearchData
from factory.utils.logger import factory_logger


class ResearchAgent:
    """Project Researcher ensuring technical feasibility and security boundaries."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def research(self, idea_data: Dict[str, Any]) -> ResearchData:
        """Perform deep feasibility and architectural constraint analysis."""
        factory_logger.info("Researching technical feasibility & stack requirements")

        system_prompt = (
            "You are the Principal Staff Researcher at Daily Project Factory.\n"
            "Analyze the project concept for autonomous buildability, security, and testing.\n"
            "CRITICAL PRINCIPLES:\n"
            "1. Favor the simplest appropriate technology stack (prefer standard Python libraries, FastAPI, Pydantic, pytest).\n"
            "2. Ensure all external dependencies are installable via pip without heavy OS binaries.\n"
            "3. Identify security risks (payload injection, unsanitized input, secrets leak).\n"
            "4. Specify strict automated testing requirements (unit, integration, mock fixtures).\n"
            "Output MUST be valid JSON matching the schema."
        )

        user_prompt = f"""
Project Name: {idea_data.get('project_name')}
Category: {idea_data.get('category')}
Description: {idea_data.get('description')}
Problem Statement: {idea_data.get('problem_statement')}
Features: {json.dumps(idea_data.get('features', []))}
Target Technologies: {json.dumps(idea_data.get('technologies', []))}

Perform technical research and output JSON in this structure:
{{
  "feasibility": "Assessment of feasibility for autonomous generation and verification",
  "required_technologies": ["Python >= 3.10", "FastAPI", "Pydantic", "pytest"],
  "external_apis": [],
  "libraries": ["fastapi", "pydantic", "pytest", "uvicorn", "httpx"],
  "datasets": ["Description of synthesized domain data fixtures"],
  "architecture_overview": "Summary of module interaction and data flow",
  "implementation_challenges": [
    "Challenge 1",
    "Challenge 2"
  ],
  "security_considerations": [
    "Input validation with Pydantic schemas",
    "Environment variable isolation for secrets"
  ],
  "testing_requirements": [
    "Pytest unit tests for core logic",
    "FastAPI TestClient integration tests"
  ]
}}
"""
        res_dict = self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.4,
        )
        research = ResearchData.model_validate(res_dict)
        return research

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        research = self.research(idea)
        state["research"] = research.model_dump()
        state["project_status"] = "researching"
        state["logs"].append(f"Completed research for {idea.get('project_name')}")
        return state

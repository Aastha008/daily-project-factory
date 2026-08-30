"""
Agent 6: README Agent
Generates comprehensive, professional, portfolio-grade GitHub README.md
documentation accurately reflecting the project's actual implementation.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from factory.llm.base import LLMProvider
from factory.state import ProjectState
from factory.utils.logger import factory_logger


class ReadmeAgent:
    """Technical Documentation Specialist crafting top-tier GitHub READMEs."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_readme(
        self,
        idea: Dict[str, Any],
        architecture: Dict[str, Any],
        files: Dict[str, str],
    ) -> str:
        """Generate comprehensive Markdown documentation."""
        factory_logger.info("Generating professional GitHub README.md")

        system_prompt = (
            "You are a Principal Technical Writer at Daily Project Factory.\n"
            "Generate an elite, complete, beautiful GitHub README.md in Markdown.\n"
            "SECTIONS TO INCLUDE:\n"
            "1. Title, badges (Python, CI, License, Code Style), and compelling description.\n"
            "2. Problem Statement & Target Audience.\n"
            "3. Key Features (only real features implemented in the code).\n"
            "4. Architecture & System Design.\n"
            "5. Technology Stack.\n"
            "6. Installation & Virtual Environment Setup.\n"
            "7. Environment Variables Configuration.\n"
            "8. Usage: CLI commands & API endpoints.\n"
            "9. Automated Testing Instructions (pytest commands).\n"
            "10. Project Structure tree.\n"
            "11. Roadmap / Future Enhancements.\n"
            "12. License (MIT).\n"
            "OUTPUT: Output the raw Markdown content directly."
        )

        file_names = list(files.keys())
        user_prompt = f"""
Project Name: {idea.get('project_name')}
Category: {idea.get('category')}
Description: {idea.get('description')}
Problem Statement: {idea.get('problem_statement')}
Features: {json.dumps(idea.get('features', []))}
Target Technologies: {json.dumps(idea.get('technologies', []))}
Architecture Modules: {json.dumps(architecture.get('modules', []))}
Files Present in Codebase: {json.dumps(file_names)}

Write the full GitHub README.md now.
"""
        raw_readme = self.llm.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        # Strip any accidental wrapping ```markdown ... ```
        cleaned = raw_readme.strip()
        if cleaned.startswith("```markdown"):
            cleaned = cleaned[11:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        arch = state.get("architecture") or {}
        files = state.get("files") or {}

        readme_content = self.generate_readme(idea, arch, files)
        state["readme_content"] = readme_content
        state["files"]["README.md"] = readme_content
        state["logs"].append("Generated README.md")
        return state

"""
Agent 2: Idea Generator Agent
Generates unique, category-aligned, portfolio-grade project concepts
and ensures non-duplication against past projects in data/projects.json.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from slugify import slugify
from factory.agents.history_manager import HistoryManagerAgent
from factory.config import WEEKLY_SCHEDULE
from factory.llm.base import LLMProvider
from factory.state import IdeaData, ProjectState
from factory.utils.logger import factory_logger


class IdeaGeneratorAgent:
    """Idea Generator crafting non-trivial, portfolio-worthy software project ideas."""

    def __init__(self, llm: LLMProvider, history_manager: Optional[HistoryManagerAgent] = None):
        self.llm = llm
        self.history_manager = history_manager or HistoryManagerAgent()

    def generate(self, category: str, custom_idea_prompt: Optional[str] = None) -> IdeaData:
        """Generate a unique project idea for the specified category."""
        factory_logger.step("Generating project idea")

        past_projects = self.history_manager.load_history()
        past_summaries = [
            f"- {p.get('project_name')}: {p.get('description')}"
            for p in past_projects[-10:]
        ]
        history_context = "\n".join(past_summaries) if past_summaries else "None (Initial Project)"

        category_info = next(
            (info for day, info in WEEKLY_SCHEDULE.items() if info["category"].lower() == category.lower()),
            {"focus": f"{category} software engineering", "tech_hints": ["Python", "FastAPI", "pytest"]}
        )

        system_prompt = (
            "You are the Lead Innovation Architect at Daily Project Factory.\n"
            "Your mission is to invent a realistic, production-worthy, innovative software project "
            "that demonstrates elite engineering craftsmanship.\n"
            "Rules:\n"
            "1. NEVER suggest trivial beginner toys (no basic calculators, no plain todo lists, no generic chatbots).\n"
            "2. Ensure the idea is completely self-contained, realistic to build and test automatically with pytest.\n"
            "3. The project MUST solve a concrete developer or business problem.\n"
            "4. Strictly output valid JSON matching the requested structure."
        )

        user_prompt = f"""
Current Category: {category}
Category Focus: {category_info['focus']}
Recommended Technologies: {', '.join(category_info['tech_hints'])}

Recent Projects from History (DO NOT REPEAT OR CLOSELY IMITATE THESE):
{history_context}

{f"User Preference / Guidance: {custom_idea_prompt}" if custom_idea_prompt else ""}

Generate a high-value software project concept. Output JSON in this exact structure:
{{
  "project_name": "Project Title",
  "category": "{category}",
  "description": "2-3 sentence technical overview of what the application does and why it matters.",
  "problem_statement": "Concrete problem or inefficiency being solved.",
  "target_users": ["User Role 1", "User Role 2"],
  "features": [
    "Core feature 1 (functional)",
    "Core feature 2 (data processing / engine)",
    "Core feature 3 (API or CLI interface)",
    "Core feature 4 (telemetry or validation)"
  ],
  "optional_advanced_features": [
    "Advanced feature 1",
    "Advanced feature 2"
  ],
  "technologies": ["Python", "FastAPI", "Pydantic", "pytest", "etc"]
}}
"""
        # Generate with retry/uniqueness check
        idea_dict = {}
        for attempt in range(3):
            idea_dict = self.llm.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.75 + (attempt * 0.1),
            )
            name = idea_dict.get("project_name", f"{category} Engine")
            desc = idea_dict.get("description", "")

            is_unique, reason = self.history_manager.check_uniqueness(name, desc)
            if is_unique:
                break
            factory_logger.warning(f"Idea '{name}' flagged: {reason}. Regenerating (attempt {attempt + 1})...")

        # Fallback defaults if LLM omitted fields
        if "project_name" not in idea_dict:
            idea_dict["project_name"] = f"{category} Autonomous Core"
        if "category" not in idea_dict:
            idea_dict["category"] = category
        if "description" not in idea_dict:
            idea_dict["description"] = f"Production-grade {category} engineering system."
        if "problem_statement" not in idea_dict:
            idea_dict["problem_statement"] = "Streamlining automated developer workflows."
        if "features" not in idea_dict:
            idea_dict["features"] = ["Core engine", "Validation schemas", "API endpoints"]
        if "technologies" not in idea_dict:
            idea_dict["technologies"] = ["Python", "FastAPI", "Pydantic", "pytest"]

        idea_dict["repository_slug"] = slugify(idea_dict["project_name"])
        idea = IdeaData.model_validate(idea_dict)

        factory_logger.step(f"Project: {idea.project_name}")
        factory_logger.info(f"Slug: {idea.repository_slug}")
        return idea

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        category = state.get("category", "Python")
        idea = self.generate(category)
        state["idea"] = idea.model_dump()
        state["project_status"] = "ideating"
        state["logs"].append(f"Generated idea: {idea.project_name}")
        return state

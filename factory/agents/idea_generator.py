"""
Agent 2: Idea Generator Agent
Generates unique, category-aligned, portfolio-grade project concepts
with simple, realistic, human-readable repository names.
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
from factory.utils.naming import (
    derive_name_from_functionality,
    is_valid_repo_slug,
    resolve_unique_slug,
    slug_to_title,
)


class IdeaGeneratorAgent:
    """Idea Generator crafting realistic, human-named, portfolio-worthy software projects."""

    def __init__(self, llm: LLMProvider, history_manager: Optional[HistoryManagerAgent] = None):
        self.llm = llm
        self.history_manager = history_manager or HistoryManagerAgent()

    def generate(self, category: str, custom_idea_prompt: Optional[str] = None) -> IdeaData:
        """Generate a unique project idea with a realistic, human-readable name."""
        factory_logger.step("Generating project idea")

        past_projects = self.history_manager.load_history()
        past_summaries = [
            f"- {p.get('project_name')} ({p.get('repository')}): {p.get('description')}"
            for p in past_projects[-10:]
        ]
        history_context = "\n".join(past_summaries) if past_summaries else "None (Initial Project)"
        existing_slugs = self.history_manager.get_existing_slugs()

        category_info = next(
            (info for day, info in WEEKLY_SCHEDULE.items() if info["category"].lower() == category.lower()),
            {"focus": f"{category} software engineering", "tech_hints": ["Python", "FastAPI", "pytest"]}
        )

        system_prompt = (
            "You are the Lead Innovation Architect at Daily Project Factory.\n"
            "Your mission is to invent a realistic, production-worthy, clean software project "
            "that demonstrates practical engineering craftsmanship.\n\n"
            "PROJECT NAMING RULES (CRITICAL):\n"
            "1. Give the project a SIMPLE, REALISTIC, HUMAN-READABLE title (2–4 words).\n"
            "   - GOOD: Expense Tracker, Habit Tracker, PDF Summarizer, Resume Analyzer, Study Planner, "
            "Movie Finder, Weather Dashboard, API Tester, Markdown Editor, File Organizer, Invoice Generator, "
            "Quiz Maker, Recipe Finder, Meeting Notes, Password Manager, Job Tracker\n"
            "   - BAD: NeuralExpenseOptimization, HyperHabitNexus, SmartResumeEngine, AI-powered-Dynamic-Workflow-Framework, "
            "QuantumFileManager, NextGenIntelligentTaskEngine\n"
            "2. The name MUST describe WHAT the project does, NOT the technology used to build it.\n"
            "   - GOOD: expense-tracker (NOT react-finance-dashboard, NOT AIExpenseManager, NOT NeuralBudgetEngine)\n"
            "   - GOOD: pdf-summarizer (NOT AI-Powered-Document-Intelligence, NOT SmartPDFEngine)\n"
            "   - GOOD: interview-coach (NOT AIInterviewOptimizationEngine)\n"
            "3. FORBIDDEN WORDS: NEVER use artificial AI marketing buzzwords: neural, quantum, hyper, nexus, smart, "
            "ultra, nextgen, advanced, intelligent, dynamic, revolutionary, pro, x, engine, framework, matrix, sentinel, pulse, forge, platform.\n"
            "4. Do NOT force the word 'AI' into the name just because the project uses AI.\n"
            "5. Do NOT append random numbers, dates, UUIDs, or meaningless suffixes.\n"
            "6. Output the repository slug as lowercase kebab-case in 'repository_slug' (e.g. 'expense-tracker').\n"
            "7. Output valid JSON matching the exact schema."
        )

        user_prompt = f"""
Current Category: {category}
Category Focus: {category_info['focus']}
Recommended Technologies: {', '.join(category_info['tech_hints'])}

Recent Projects from History (DO NOT REPEAT OR CLOSELY IMITATE THESE):
{history_context}

{f"User Preference / Guidance: {custom_idea_prompt}" if custom_idea_prompt else ""}

Generate a high-value software project concept with a clean, developer-friendly name.
Output JSON in this exact structure:
{{
  "project_name": "Concise Project Title (e.g. Expense Tracker)",
  "repository_slug": "lowercase-kebab-case-slug (e.g. expense-tracker)",
  "category": "{category}",
  "description": "2-3 sentence technical overview of what the application does and why it matters.",
  "problem_statement": "Concrete problem or inefficiency being solved.",
  "target_users": ["User Role 1", "User Role 2"],
  "features": [
    "Core feature 1 (functional)",
    "Core feature 2 (data processing / logic)",
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
        # Generate with retry and uniqueness/naming validation
        idea_dict = {}
        for attempt in range(3):
            idea_dict = self.llm.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7 + (attempt * 0.1),
            )

            raw_name = idea_dict.get("project_name", "")
            raw_slug = idea_dict.get("repository_slug", "")
            desc = idea_dict.get("description", "")
            problem = idea_dict.get("problem_statement", "")

            # 1. Derive and sanitize title and slug based on actual purpose
            clean_title, clean_slug = derive_name_from_functionality(
                project_name=raw_slug or raw_name,
                description=desc,
                problem_statement=problem,
                category=category,
            )

            # 2. Resolve uniqueness against past repository slugs
            unique_slug = resolve_unique_slug(clean_slug, existing_slugs, category=category)
            unique_title = slug_to_title(unique_slug)

            idea_dict["project_name"] = unique_title
            idea_dict["repository_slug"] = unique_slug

            # 3. Check uniqueness in history ledger
            is_unique, reason = self.history_manager.check_uniqueness(
                project_name=unique_title,
                description=desc,
                repository_slug=unique_slug,
            )

            if is_unique:
                break
            factory_logger.warning(f"Idea '{unique_title}' flagged: {reason}. Regenerating (attempt {attempt + 1})...")

        # Fallback defaults if LLM omitted fields
        if "description" not in idea_dict or not idea_dict["description"]:
            idea_dict["description"] = f"Production-grade {category} engineering system."
        if "problem_statement" not in idea_dict or not idea_dict["problem_statement"]:
            idea_dict["problem_statement"] = "Streamlining automated developer workflows."
        if "category" not in idea_dict:
            idea_dict["category"] = category
        if "features" not in idea_dict or not idea_dict["features"]:
            idea_dict["features"] = ["Core application logic", "Data validation schemas", "API endpoints"]
        if "technologies" not in idea_dict or not idea_dict["technologies"]:
            idea_dict["technologies"] = ["Python", "FastAPI", "Pydantic", "pytest"]

        # Final quality assurance validation on the naming
        final_slug = idea_dict.get("repository_slug")
        if not final_slug or not is_valid_repo_slug(final_slug)[0]:
            clean_title, clean_slug = derive_name_from_functionality(
                project_name=idea_dict.get("project_name", ""),
                description=idea_dict.get("description", ""),
                problem_statement=idea_dict.get("problem_statement", ""),
                category=category,
            )
            final_slug = resolve_unique_slug(clean_slug, existing_slugs, category=category)
            idea_dict["repository_slug"] = final_slug
            idea_dict["project_name"] = slug_to_title(final_slug)

        idea = IdeaData.model_validate(idea_dict)

        factory_logger.step(f"Project: {idea.project_name}")
        factory_logger.info(f"Repository Slug: {idea.repository_slug}")
        return idea

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        category = state.get("category", "Python")
        idea = self.generate(category)
        state["idea"] = idea.model_dump()
        state["project_status"] = "ideating"
        state["logs"].append(f"Generated idea: {idea.project_name} ({idea.repository_slug})")
        return state

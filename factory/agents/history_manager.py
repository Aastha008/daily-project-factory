"""
Agent 13: Project History Agent
Maintains persistent ledger of generated projects in data/projects.json,
checks uniqueness, and prevents thematic repetition.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from factory.config import settings
from factory.state import ProjectState
from factory.utils.logger import factory_logger


class HistoryManagerAgent:
    """Project History Manager and Uniqueness Validator."""

    def __init__(self, projects_file: Optional[Path] = None):
        self.projects_file = projects_file or settings.projects_file
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.projects_file.exists():
            self._init_empty_history()

    def _init_empty_history(self) -> None:
        """Create empty history ledger if none exists."""
        with open(self.projects_file, "w", encoding="utf-8") as f:
            json.dump({"projects": []}, f, indent=2)

    def load_history(self) -> List[Dict[str, Any]]:
        """Read all past project records."""
        try:
            with open(self.projects_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("projects", [])
        except Exception as exc:
            factory_logger.warning(f"Could not load history ledger: {exc}. Starting fresh.")
            return []

    def save_project(
        self,
        date: str,
        day: str,
        category: str,
        project_name: str,
        repository: str,
        github_url: str,
        description: str,
        status: str = "published",
    ) -> None:
        """Append published project record to history ledger."""
        history = self.load_history()

        record = {
            "date": date,
            "day": day,
            "category": category,
            "project_name": project_name,
            "repository": repository,
            "github_url": github_url,
            "status": status,
            "description": description,
        }

        # Avoid exact duplicate entries
        history = [p for p in history if p.get("repository") != repository]
        history.append(record)

        with open(self.projects_file, "w", encoding="utf-8") as f:
            json.dump({"projects": history}, f, indent=2)

        factory_logger.info(f"Updated project history in {self.projects_file.name}")

    def tokenize(self, text: str) -> set[str]:
        """Convert text into cleaned alphanumeric tokens for similarity comparison."""
        tokens = re.findall(r"\b[a-zA-Z0-9_]{3,}\b", text.lower())
        stopwords = {"the", "and", "for", "with", "from", "that", "this", "app", "project", "tool"}
        return {t for t in tokens if t not in stopwords}

    def check_uniqueness(self, project_name: str, description: str, threshold: float = 0.55) -> Tuple[bool, str]:
        """
        Check if the proposed project idea is too similar to any previously built project.
        Returns (is_unique, reason).
        """
        history = self.load_history()
        if not history:
            return True, "History is empty. Idea is unique."

        new_tokens = self.tokenize(f"{project_name} {description}")

        for past in history:
            past_name = past.get("project_name", "")
            past_desc = past.get("description", "")

            # Exact name match
            if project_name.lower().strip() == past_name.lower().strip():
                return False, f"Exact project name match with past project from {past.get('date')}: '{past_name}'"

            # Jaccard token similarity
            past_tokens = self.tokenize(f"{past_name} {past_desc}")
            if not past_tokens or not new_tokens:
                continue

            intersection = len(new_tokens.intersection(past_tokens))
            union = len(new_tokens.union(past_tokens))
            similarity = float(intersection) / float(union) if union > 0 else 0.0

            if similarity > threshold:
                return False, f"High thematic similarity ({similarity:.2f}) to '{past_name}' ({past.get('date')})"

        return True, "Idea passed uniqueness validation."

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution for saving history."""
        github_info = state.get("github_info") or {}
        idea = state.get("idea") or {}
        status = github_info.get("status", "published")

        if status in ["published", "skipped"]:
            self.save_project(
                date=state.get("date", ""),
                day=state.get("day", ""),
                category=state.get("category", ""),
                project_name=idea.get("project_name", "Untitled Project"),
                repository=github_info.get("repository_name", "untitled-project"),
                github_url=github_info.get("github_url", "https://github.com"),
                description=idea.get("description", ""),
                status=status,
            )
            state["history_updated"] = True
        return state

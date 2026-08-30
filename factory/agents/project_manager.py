"""
Agent 1: Project Manager Agent
Determines today's date, day of the week, project category,
coordinates workflow state, and initializes project lifecycle.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Optional
from factory.config import WEEKLY_SCHEDULE, settings
from factory.state import ProjectState
from factory.utils.logger import factory_logger


class ProjectManagerAgent:
    """Project Manager coordinating the daily software engineering workflow."""

    def __init__(self, override_category: Optional[str] = None, override_day: Optional[str] = None):
        self.override_category = override_category
        self.override_day = override_day

    def execute(self, state: Optional[ProjectState] = None) -> ProjectState:
        """Initialize and populate project metadata."""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        day_str = self.override_day or now.strftime("%A")

        # Resolve category
        if self.override_category:
            category = self.override_category
        else:
            schedule_info = WEEKLY_SCHEDULE.get(day_str, WEEKLY_SCHEDULE["Monday"])
            category = schedule_info["category"]

        factory_logger.step("Starting Daily Project Factory")
        factory_logger.step(f"Category: {category}")
        factory_logger.info(f"Date: {date_str} ({day_str})")

        new_state: ProjectState = {
            "date": date_str,
            "day": day_str,
            "category": category,
            "project_status": "planning",
            "files": {},
            "debug_attempts": 0,
            "debug_history": [],
            "logs": [f"Initialized workflow for {category} on {date_str}"],
            "start_time": now.timestamp(),
        }

        if state:
            new_state.update(state)
            new_state["date"] = date_str
            new_state["day"] = day_str
            new_state["category"] = category

        return new_state

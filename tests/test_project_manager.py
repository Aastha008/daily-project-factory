"""
Tests for ProjectManagerAgent and day-to-category resolution.
"""

import pytest
from factory.agents.project_manager import ProjectManagerAgent
from factory.config import WEEKLY_SCHEDULE


def test_weekly_schedule_mapping():
    """Verify all 7 days have valid, distinct categories per prompt specs."""
    expected_categories = {
        "Monday": "Python",
        "Tuesday": "AI",
        "Wednesday": "Web Development",
        "Thursday": "Data Analytics",
        "Friday": "Machine Learning",
        "Saturday": "Automation",
        "Sunday": "Full Stack",
    }

    for day, expected_cat in expected_categories.items():
        assert day in WEEKLY_SCHEDULE
        assert WEEKLY_SCHEDULE[day]["category"] == expected_cat
        assert len(WEEKLY_SCHEDULE[day]["focus"]) > 0
        assert len(WEEKLY_SCHEDULE[day]["tech_hints"]) > 0


def test_project_manager_execution_default():
    """Verify PM agent initializes correct state for any given day."""
    pm = ProjectManagerAgent(override_day="Monday")
    state = pm.execute()

    assert state["day"] == "Monday"
    assert state["category"] == "Python"
    assert state["project_status"] == "planning"
    assert "date" in state
    assert state["debug_attempts"] == 0


def test_project_manager_category_override():
    """Verify PM agent respects explicit category override."""
    pm = ProjectManagerAgent(override_category="Machine Learning")
    state = pm.execute()

    assert state["category"] == "Machine Learning"
    assert state["project_status"] == "planning"

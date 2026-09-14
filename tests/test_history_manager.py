"""
Tests for HistoryManagerAgent, persistence, and uniqueness checking.
"""

import json
import pytest
from factory.agents.history_manager import HistoryManagerAgent


def test_history_persistence_and_uniqueness(tmp_path):
    """Verify history loading, saving, and duplicate/similarity detection."""
    test_file = tmp_path / "test_projects.json"
    history_agent = HistoryManagerAgent(projects_file=test_file)

    # Initial load should be empty
    assert history_agent.load_history() == []
    assert history_agent.get_existing_slugs() == set()

    # Save a project with clean human name
    history_agent.save_project(
        date="2026-08-30",
        day="Sunday",
        category="Full Stack",
        project_name="Expense Tracker",
        repository="expense-tracker",
        github_url="https://github.com/mock/expense-tracker",
        description="Automated receipt scanner and expense tracker with budget forecasting.",
    )

    records = history_agent.load_history()
    assert len(records) == 1
    assert records[0]["project_name"] == "Expense Tracker"
    assert "expense-tracker" in history_agent.get_existing_slugs()

    # Exact name check should fail uniqueness
    is_unique, reason = history_agent.check_uniqueness(
        "Expense Tracker", "Some other description"
    )
    assert not is_unique
    assert "Exact project name match" in reason

    # Exact repository slug duplicate check should fail uniqueness
    is_unique, reason = history_agent.check_uniqueness(
        "Budget Tool", "Some other description", repository_slug="expense-tracker"
    )
    assert not is_unique
    assert "slug duplicate" in reason

    # Brand new unique project should pass
    is_unique, reason = history_agent.check_uniqueness(
        "Cluster Monitor", "Distributed cluster node metrics and latency watcher", repository_slug="cluster-monitor"
    )
    assert is_unique
    assert "passed" in reason

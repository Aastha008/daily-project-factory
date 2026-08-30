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

    # Save a project
    history_agent.save_project(
        date="2026-08-30",
        day="Sunday",
        category="Full Stack",
        project_name="Smart Expense Analyzer",
        repository="smart-expense-analyzer",
        github_url="https://github.com/mock/smart-expense-analyzer",
        description="Automated receipt scanner and expense tracker with budget forecasting.",
    )

    records = history_agent.load_history()
    assert len(records) == 1
    assert records[0]["project_name"] == "Smart Expense Analyzer"

    # Exact name check should fail uniqueness
    is_unique, reason = history_agent.check_uniqueness(
        "Smart Expense Analyzer", "Some other description"
    )
    assert not is_unique
    assert "Exact project name match" in reason

    # Brand new unique project should pass
    is_unique, reason = history_agent.check_uniqueness(
        "Kubernetes Health Sentry", "Distributed cluster node metrics and latency watcher"
    )
    assert is_unique
    assert "passed" in reason

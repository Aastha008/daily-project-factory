"""
Tests for GitHubPublisherAgent in local / dry-run mode.
"""

import pytest
from pathlib import Path
from factory.agents.github_publisher import GitHubPublisherAgent


def test_github_publisher_dry_run(tmp_path):
    """Verify GitHub publisher initializes local repo and commits code in dry-run mode."""
    publisher = GitHubPublisherAgent(dry_run=True, skip_github=True)

    project_dir = tmp_path / "test-repo"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    (project_dir / "main.py").write_text("print('test')\n", encoding="utf-8")

    result = publisher.publish(
        project_dir=project_dir,
        project_name="Test Repo",
        repo_slug="test-repo",
        description="A test repository",
        topics=["python", "testing"],
    )

    assert result.status == "published"
    assert result.repository_name == "test-repo"
    assert "test-repo" in result.github_url
    assert (project_dir / ".git").exists()

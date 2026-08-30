"""
Tests for IdeaGeneratorAgent.
"""

import pytest
from factory.agents.idea_generator import IdeaGeneratorAgent
from factory.agents.history_manager import HistoryManagerAgent
from factory.llm.mock_provider import MockLLMProvider


def test_idea_generator_with_mock_llm(tmp_path):
    """Verify idea generation produces valid IdeaData schemas."""
    mock_llm = MockLLMProvider()
    test_file = tmp_path / "test_projects.json"
    history = HistoryManagerAgent(projects_file=test_file)
    idea_agent = IdeaGeneratorAgent(llm=mock_llm, history_manager=history)

    for cat in ["Python", "AI", "Web Development", "Data Analytics", "Machine Learning", "Automation", "Full Stack"]:
        idea = idea_agent.generate(category=cat)
        assert idea.project_name
        assert idea.category == cat
        assert idea.description
        assert len(idea.features) >= 2
        assert len(idea.technologies) >= 2
        assert idea.repository_slug
        assert " " not in idea.repository_slug

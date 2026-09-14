"""
Tests for IdeaGeneratorAgent and human naming validation.
"""

import pytest
from factory.agents.idea_generator import IdeaGeneratorAgent
from factory.agents.history_manager import HistoryManagerAgent
from factory.llm.mock_provider import MockLLMProvider
from factory.utils.naming import (
    is_valid_repo_slug,
    derive_name_from_functionality,
    resolve_unique_slug,
    slug_to_title,
)


def test_idea_generator_with_mock_llm(tmp_path):
    """Verify idea generation produces valid IdeaData schemas with clean human names."""
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

        # Validate that generated slug meets strict human naming rules
        is_valid, reason = is_valid_repo_slug(idea.repository_slug)
        assert is_valid, f"Generated slug '{idea.repository_slug}' failed validation: {reason}"


def test_naming_validation_rules():
    """Verify is_valid_repo_slug enforces human developer naming rules."""
    good_examples = [
        "expense-tracker",
        "habit-tracker",
        "pdf-chat",
        "resume-analyzer",
        "study-planner",
        "movie-finder",
        "weather-dashboard",
        "api-tester",
        "markdown-editor",
        "file-organizer",
        "invoice-generator",
        "quiz-maker",
        "recipe-finder",
        "meeting-notes",
        "password-manager",
        "job-tracker",
    ]
    for slug in good_examples:
        is_valid, reason = is_valid_repo_slug(slug)
        assert is_valid, f"Expected '{slug}' to be valid, but got: {reason}"

    bad_examples = [
        "neural-expense-optimization",
        "hyper-habit-nexus",
        "smart-resume-engine",
        "ai-workflow-framework",
        "quantum-file-manager",
        "nextgen-task-engine",
        "ultra-data-matrix",
        "dynamic-portal",
        "awesome-project",
        "cool-app",
        "my-project",
        "task-12345",
        "project-v2",
        "tool-a1b2c3d4",
    ]
    for slug in bad_examples:
        is_valid, _ = is_valid_repo_slug(slug)
        assert not is_valid, f"Expected '{slug}' to be rejected as an invalid buzzword/vague name"


def test_derive_name_from_functionality():
    """Verify derive_name_from_functionality converts artificial names to clean human names."""
    # Test 1: Expense tracking app with buzzword title
    title, slug = derive_name_from_functionality(
        project_name="Neural Expense Optimization",
        description="A lightweight web application for tracking monthly spending and receipts.",
        problem_statement="Users find it hard to track personal budget expenses.",
        category="Full Stack",
    )
    assert slug == "expense-tracker"
    assert title == "Expense Tracker"

    # Test 2: Resume analysis with buzzwords
    title, slug = derive_name_from_functionality(
        project_name="Smart Resume Engine",
        description="Analyzes CVs and resumes against job descriptions.",
        problem_statement="Job applicants need feedback on their resumes.",
        category="Python",
    )
    assert slug == "resume-analyzer"
    assert title == "Resume Analyzer"

    # Test 3: PDF summarizer
    title, slug = derive_name_from_functionality(
        project_name="Quantum Document Intelligence Nexus",
        description="Summarizes PDF documents and extracts key highlights.",
        problem_statement="Reading long PDF reports takes hours.",
        category="AI",
    )
    assert slug == "pdf-summarizer"
    assert title == "PDF Summarizer"


def test_resolve_unique_slug_natural_differentiators():
    """Verify duplicate slugs get natural differentiators without appending random numbers."""
    existing = {"expense-tracker"}

    unique_slug = resolve_unique_slug("expense-tracker", existing)
    assert unique_slug != "expense-tracker"
    assert not any(c.isdigit() for c in unique_slug), f"Slug '{unique_slug}' should not contain numbers"
    assert unique_slug in [
        "simple-expense-tracker",
        "minimal-expense-tracker",
        "daily-expense-tracker",
        "personal-expense-tracker",
        "quick-expense-tracker",
        "lite-expense-tracker",
    ]

    # Multiple collisions still get natural prefixes
    existing.add("simple-expense-tracker")
    existing.add("minimal-expense-tracker")
    second_unique = resolve_unique_slug("expense-tracker", existing)
    assert second_unique not in existing
    assert not any(c.isdigit() for c in second_unique)

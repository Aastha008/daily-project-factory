"""
Summary report generator for Daily Project Factory executions.
Matches the official Daily Project Factory specification.
"""

from __future__ import annotations

import sys
from typing import Any, Dict
from factory.state import ProjectState


def generate_final_report(state: ProjectState, use_ascii_checkmarks: bool = False) -> str:
    """Format structured state into standard Daily Project Factory report."""
    date_str = state.get("date", "N/A")
    day_str = state.get("day", "N/A")
    category_str = state.get("category", "N/A")

    idea = state.get("idea") or {}
    project_name = idea.get("project_name", "N/A")
    description = idea.get("description", "N/A")
    tech_stack = ", ".join(idea.get("technologies", [])) or "Python, Standard Libraries"

    test_res = state.get("test_results") or {}
    tests_passed = test_res.get("tests_passed", 0)
    tests_failed = test_res.get("tests_failed", 0)

    code_review = state.get("code_review") or {}
    review_score = code_review.get("score", 0.0)

    github_info = state.get("github_info") or {}
    repo_name = github_info.get("repository_name", "N/A")
    repo_url = github_info.get("github_url", "N/A")
    status_str = github_info.get("status", state.get("project_status", "UNKNOWN")).upper()

    chk = "[x]" if use_ascii_checkmarks else "✓"

    report = f"""
========================================
DAILY PROJECT FACTORY
========================================

Date: {date_str}
Day: {day_str}
Category: {category_str}

Project: {project_name}
Description: {description}

Tech Stack: {tech_stack}

Agents Executed:
{chk} Planner
{chk} Idea Generator
{chk} Researcher
{chk} Architect
{chk} Coder
{chk} Tester
{chk} Debugger
{chk} Reviewer
{chk} GitHub Publisher

Tests:
Passed: {tests_passed}
Failed: {tests_failed}

Code Review:
Score: {review_score:.1f}/10

GitHub:
Repository: {repo_name}
URL: {repo_url}

Status: {status_str}
========================================
"""
    return report.strip()

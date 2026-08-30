"""
Agent 9: Code Review Agent
Performs comprehensive quality inspection, static security screening (secrets & credentials),
and functional audit before granting publishing approval.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from factory.llm.base import LLMProvider
from factory.state import ProjectState, ReviewResult
from factory.utils.logger import factory_logger


class CodeReviewAgent:
    """Security Auditor & Lead Reviewer scoring quality and gating repository publishing."""

    SECRET_PATTERNS = [
        re.compile(r"(?i)(password|passwd|secret|api_key|apikey|token|auth_token)\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]"),
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
        re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
        re.compile(r"sk-[A-Za-z0-9]{32,}"),
        re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    ]

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def scan_for_secrets(self, files: Dict[str, str]) -> List[str]:
        """Perform regex scan for leaked credentials and hardcoded secrets."""
        leaks: List[str] = []
        for filename, content in files.items():
            if filename in [".env.example"]:
                continue
            for line_no, line in enumerate(content.splitlines(), start=1):
                # Ignore placeholder strings
                if "your-" in line or "your_" in line or "example" in line:
                    continue
                for pattern in self.SECRET_PATTERNS:
                    if pattern.search(line):
                        leaks.append(f"Security Alert in {filename} (line {line_no}): Potential hardcoded credential detected")
        return leaks

    def review_project(
        self,
        idea: Dict[str, Any],
        files: Dict[str, str],
        test_results: Dict[str, Any],
    ) -> ReviewResult:
        """Evaluate project quality, security, and documentation."""
        factory_logger.step("Code review")

        # 1. Static security check
        security_leaks = self.scan_for_secrets(files)
        if security_leaks:
            factory_logger.error(f"Security check failed: {security_leaks[0]}")
            return ReviewResult(
                approved=False,
                score=3.0,
                security_verdict="fail",
                issues=security_leaks,
                feedback="Critical security violation: Hardcoded secrets or tokens discovered in source files.",
            )

        # 2. LLM rubric evaluation
        system_prompt = (
            "You are the Head of Engineering at Daily Project Factory.\n"
            "Conduct a strict, professional code review of the generated software project.\n"
            "EVALUATION CRITERIA:\n"
            "1. Code Quality & Modularity (Pythonic style, typing, clean functions)\n"
            "2. Security & Hygiene (Zero secrets, .gitignore present, input validation)\n"
            "3. Functionality & Tests (Real working logic, comprehensive test suite)\n"
            "4. Documentation (Clear README, setup guide, API details)\n"
            "SCORE: Numerical score from 1.0 to 10.0.\n"
            "APPROVAL: Set approved to true if score >= 7.5 and no critical blockers exist.\n"
            "Output MUST be valid JSON matching the schema."
        )

        code_summary = {
            name: (content[:500] + "..." if len(content) > 500 else content)
            for name, content in files.items()
        }

        user_prompt = f"""
Project Name: {idea.get('project_name')}
Category: {idea.get('category')}
Description: {idea.get('description')}
Tests Passed: {test_results.get('tests_passed', 0)} / {test_results.get('tests_run', 0)}

Codebase Snippets:
{json.dumps(code_summary, indent=2)}

Perform code review and return JSON in this schema:
{{
  "approved": true,
  "score": 8.8,
  "security_verdict": "pass",
  "strengths": [
    "Clean domain modeling with Pydantic",
    "Proper test coverage"
  ],
  "issues": [],
  "feedback": "Overall assessment summary"
}}
"""
        review_dict = self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        review = ReviewResult.model_validate(review_dict)

        if review.approved:
            factory_logger.success(f"Review approved (Score: {review.score}/10)")
        else:
            factory_logger.warning(f"Review rejected (Score: {review.score}/10). Issues: {len(review.issues)}")

        return review

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        files = state.get("files") or {}
        test_res = state.get("test_results") or {}

        review = self.review_project(idea, files, test_res)
        state["code_review"] = review.model_dump()
        state["project_status"] = "reviewing"
        state["logs"].append(f"Code review completed with score {review.score}")
        return state

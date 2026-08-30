"""
Tests for CodeReviewAgent and security leak screening.
"""

import pytest
from factory.agents.code_review import CodeReviewAgent
from factory.llm.mock_provider import MockLLMProvider


def test_code_review_secret_detection():
    """Verify code review agent flags hardcoded API keys and secrets."""
    mock_llm = MockLLMProvider()
    reviewer = CodeReviewAgent(llm=mock_llm)

    # Safe files
    safe_files = {
        "src/app.py": "import os\napi_key = os.getenv('API_KEY')\n",
        ".env.example": "API_KEY=your-secret-key-here\n",
    }
    leaks = reviewer.scan_for_secrets(safe_files)
    assert len(leaks) == 0

    # Compromised file with hardcoded secret
    unsafe_files = {
        "src/config.py": "API_KEY = 'sk-1234567890abcdef1234567890abcdef'\n",
    }
    leaks = reviewer.scan_for_secrets(unsafe_files)
    assert len(leaks) >= 1
    assert "Security Alert" in leaks[0]


def test_code_review_evaluation():
    """Verify code review returns valid ReviewResult."""
    mock_llm = MockLLMProvider()
    reviewer = CodeReviewAgent(llm=mock_llm)

    idea = {"project_name": "Test App", "category": "AI", "description": "Testing RAG App"}
    files = {"src/app.py": "print('hello')\n"}
    test_res = {"tests_passed": 5, "tests_run": 5}

    result = reviewer.review_project(idea, files, test_res)
    assert result.approved is True
    assert result.score >= 7.5
    assert result.security_verdict == "pass"

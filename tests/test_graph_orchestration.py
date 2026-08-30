"""
End-to-end tests for LangGraph state machine orchestration and conditional routing.
"""

import pytest
from factory.llm.mock_provider import MockLLMProvider
from factory.workflow.graph import build_project_factory_graph, run_project_factory


def test_graph_compilation():
    """Verify that LangGraph StateGraph builds and compiles without error."""
    mock_llm = MockLLMProvider()
    app = build_project_factory_graph(llm=mock_llm, dry_run=True, skip_github=True)
    assert app is not None


def test_end_to_end_graph_execution():
    """Verify full end-to-end multi-agent execution pipeline on an AI project."""
    mock_llm = MockLLMProvider()
    final_state = run_project_factory(
        llm=mock_llm,
        override_category="AI",
        dry_run=True,
        skip_github=True,
    )

    assert final_state["category"] == "AI"
    assert "idea" in final_state
    assert "research" in final_state
    assert "architecture" in final_state
    assert "files" in final_state
    assert len(final_state["files"]) >= 5
    assert final_state["test_results"]["status"] == "passed"
    assert final_state["code_review"]["approved"] is True
    assert final_state["github_info"]["status"] == "published"
    assert final_state["history_updated"] is True

"""
LangGraph Multi-Agent Orchestration Graph for Daily Project Factory.
Assembles the complete state machine with conditional debugging loops and review gates.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Literal, Optional
from langgraph.graph import StateGraph, END

from factory.config import settings
from factory.llm.base import LLMProvider
from factory.llm.factory import get_llm_provider
from factory.state import ProjectState
from factory.agents.project_manager import ProjectManagerAgent
from factory.agents.history_manager import HistoryManagerAgent
from factory.agents.idea_generator import IdeaGeneratorAgent
from factory.agents.research import ResearchAgent
from factory.agents.architecture import ArchitectureAgent
from factory.agents.coding import CodingAgent
from factory.agents.readme import ReadmeAgent
from factory.agents.testing import TestingAgent
from factory.agents.debugger import DebuggerAgent
from factory.agents.code_review import CodeReviewAgent
from factory.agents.github_publisher import GitHubPublisherAgent
from factory.utils.logger import factory_logger


def build_project_factory_graph(
    llm: Optional[LLMProvider] = None,
    override_category: Optional[str] = None,
    override_day: Optional[str] = None,
    dry_run: bool = False,
    skip_github: bool = False,
) -> Any:
    """Build and compile the LangGraph StateGraph for the Daily Project Factory."""
    llm_instance = llm or get_llm_provider()
    history_agent = HistoryManagerAgent()

    pm_agent = ProjectManagerAgent(override_category=override_category, override_day=override_day)
    idea_agent = IdeaGeneratorAgent(llm=llm_instance, history_manager=history_agent)
    research_agent = ResearchAgent(llm=llm_instance)
    arch_agent = ArchitectureAgent(llm=llm_instance)
    coding_agent = CodingAgent(llm=llm_instance)
    readme_agent = ReadmeAgent(llm=llm_instance)
    testing_agent = TestingAgent()
    debugger_agent = DebuggerAgent(llm=llm_instance)
    review_agent = CodeReviewAgent(llm=llm_instance)
    github_agent = GitHubPublisherAgent(dry_run=dry_run, skip_github=skip_github)

    # Initialize StateGraph
    workflow = StateGraph(ProjectState)

    # Add Nodes
    workflow.add_node("project_manager", pm_agent.execute)
    workflow.add_node("idea_generator", idea_agent.execute_node)
    workflow.add_node("research", research_agent.execute_node)
    workflow.add_node("architecture", arch_agent.execute_node)
    workflow.add_node("coding", coding_agent.execute_node)
    workflow.add_node("readme", readme_agent.execute_node)
    workflow.add_node("testing", testing_agent.execute_node)
    workflow.add_node("debugger", debugger_agent.execute_node)
    workflow.add_node("code_review", review_agent.execute_node)
    workflow.add_node("github_publisher", github_agent.execute_node)
    workflow.add_node("history_manager", history_agent.execute_node)

    # Define Conditional Routing Edges
    def route_after_testing(state: ProjectState) -> Literal["code_review", "debugger", "history_manager"]:
        test_results = state.get("test_results") or {}
        status = test_results.get("status", "failed")
        attempts = state.get("debug_attempts", 0)

        if status == "passed":
            return "code_review"

        if attempts < settings.max_debug_attempts:
            return "debugger"

        factory_logger.error(
            f"Project failed tests after {attempts} debug attempts. Aborting GitHub publishing."
        )
        state["project_status"] = "failed"
        return "history_manager"

    def route_after_review(state: ProjectState) -> Literal["github_publisher", "debugger", "history_manager"]:
        review = state.get("code_review") or {}
        approved = review.get("approved", False)
        attempts = state.get("debug_attempts", 0)

        if approved:
            return "github_publisher"

        if attempts < settings.max_debug_attempts:
            factory_logger.warning("Code review rejected. Routing back to debugger.")
            return "debugger"

        factory_logger.error(
            f"Project failed code review after {attempts} attempts. Aborting GitHub publishing."
        )
        state["project_status"] = "failed"
        return "history_manager"

    # Assemble Graph Flow
    workflow.set_entry_point("project_manager")
    workflow.add_edge("project_manager", "idea_generator")
    workflow.add_edge("idea_generator", "research")
    workflow.add_edge("research", "architecture")
    workflow.add_edge("architecture", "coding")
    workflow.add_edge("coding", "readme")
    workflow.add_edge("readme", "testing")

    # Conditional Branch after Testing
    workflow.add_conditional_edges(
        "testing",
        route_after_testing,
        {
            "code_review": "code_review",
            "debugger": "debugger",
            "history_manager": "history_manager",
        },
    )

    # Debugger loops back to Testing
    workflow.add_edge("debugger", "testing")

    # Conditional Branch after Code Review
    workflow.add_conditional_edges(
        "code_review",
        route_after_review,
        {
            "github_publisher": "github_publisher",
            "debugger": "debugger",
            "history_manager": "history_manager",
        },
    )

    # Publishing and History persistence
    workflow.add_edge("github_publisher", "history_manager")
    workflow.add_edge("history_manager", END)

    # Compile the graph
    app = workflow.compile()
    return app


def run_project_factory(
    llm: Optional[LLMProvider] = None,
    override_category: Optional[str] = None,
    override_day: Optional[str] = None,
    dry_run: bool = False,
    skip_github: bool = False,
    initial_state: Optional[Dict[str, Any]] = None,
) -> ProjectState:
    """Execute the full autonomous project generation pipeline end-to-end."""
    graph = build_project_factory_graph(
        llm=llm,
        override_category=override_category,
        override_day=override_day,
        dry_run=dry_run,
        skip_github=skip_github,
    )

    inputs = initial_state or {}
    start_time = time.perf_counter()

    # Stream or invoke through graph
    final_state: ProjectState = graph.invoke(inputs)

    final_state["end_time"] = time.time()
    factory_logger.step("Complete")
    return final_state

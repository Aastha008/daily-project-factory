"""
State definitions for LangGraph multi-agent orchestration.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, TypedDict
from pydantic import BaseModel, Field


class IdeaData(BaseModel):
    project_name: str
    category: str
    description: str
    problem_statement: str
    target_users: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    optional_advanced_features: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    repository_slug: Optional[str] = None


class ResearchData(BaseModel):
    feasibility: str
    required_technologies: List[str] = Field(default_factory=list)
    external_apis: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    datasets: List[str] = Field(default_factory=list)
    architecture_overview: str
    implementation_challenges: List[str] = Field(default_factory=list)
    security_considerations: List[str] = Field(default_factory=list)
    testing_requirements: List[str] = Field(default_factory=list)


class ArchitectureData(BaseModel):
    folder_structure: Dict[str, Any] = Field(default_factory=dict)
    file_list: List[str] = Field(default_factory=list)
    modules: List[Dict[str, str]] = Field(default_factory=list)
    apis: List[Dict[str, str]] = Field(default_factory=list)
    database_schema: Optional[str] = None
    data_flow: str = ""
    env_variables: List[str] = Field(default_factory=list)
    testing_structure: str = ""


class TestResult(BaseModel):
    status: str = "pending"  # "passed", "failed", "error"
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    errors: List[str] = Field(default_factory=list)
    traceback: str = ""
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0


class ReviewResult(BaseModel):
    approved: bool = False
    score: float = 0.0
    issues: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    security_verdict: str = "pass"
    feedback: str = ""


class GitHubResult(BaseModel):
    repository_name: str = ""
    github_url: str = ""
    status: str = "pending"  # "published", "skipped", "failed"
    commit_sha: Optional[str] = None
    error: Optional[str] = None


class ProjectState(TypedDict, total=False):
    # Project Identity & Scheduling
    date: str
    day: str
    category: str
    project_status: str

    # Agent Pipeline Artifacts
    idea: Optional[Dict[str, Any]]
    research: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    files: Dict[str, str]  # filepath -> content
    readme_content: Optional[str]

    # Verification & Debugging
    test_results: Optional[Dict[str, Any]]
    debug_attempts: int
    debug_history: List[Dict[str, Any]]
    code_review: Optional[Dict[str, Any]]

    # Publishing & Registry
    github_info: Optional[Dict[str, Any]]
    history_updated: bool

    # Diagnostics & Monitoring
    project_dir: Optional[str]
    error: Optional[str]
    logs: List[str]
    start_time: float
    end_time: Optional[float]

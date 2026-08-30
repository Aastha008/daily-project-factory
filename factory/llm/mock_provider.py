"""
Offline Mock LLM Provider that supplies deterministic, high-quality,
runnable multi-file projects across all 7 categories for offline testing,
CI/CD verification, and local demonstration without requiring paid API keys.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional
from factory.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """High-fidelity Mock LLM Provider for offline end-to-end execution."""

    def __init__(self, model_name: str = "mock-gpt-4o", api_key: Optional[str] = "mock-key"):
        super().__init__(model_name=model_name, api_key=api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        combined = f"{system_prompt or ''} {prompt}".lower()

        # 1. Code Review (identified by reviewer prompt markers)
        if "conduct a strict, professional code review" in combined or "security_verdict" in combined or "code review and return json" in combined:
            return self._mock_review(prompt)

        # 2. Debugger (identified by debugging attempt markers)
        if "debugging attempt:" in combined or "principal debugger" in combined or "modified_files" in combined:
            return self._mock_debugger(prompt)

        # 3. Architecture (identified by architect prompt markers)
        if "chief software architect" in combined or "design modular architecture" in combined or "folder_structure" in combined:
            return self._mock_architecture(prompt)

        # 4. Coding (identified by coding agent prompt markers)
        if "principal software engineer" in combined or "write the complete, production-ready" in combined or "target file list:" in combined:
            return self._mock_coding(prompt)

        # 5. README (identified by technical writer prompt markers)
        if "principal technical writer" in combined or "sections to include:" in combined or "write the full github readme now" in combined:
            return self._mock_readme(prompt)

        # 6. Research (identified by researcher prompt markers)
        if "principal staff researcher" in combined or "perform technical research and output json" in combined or "feasibility" in combined:
            return self._mock_research(prompt)

        # 7. Idea Generator (identified by innovation architect markers)
        if "lead innovation architect" in combined or "current category:" in combined or "generate a high-value software project concept" in combined:
            return self._mock_idea(prompt)

        return json.dumps({"status": "ok", "message": "Mock generic response"})

    def _mock_idea(self, prompt: str) -> str:
        category = "AI"

        # Search for exact category in "Current Category: <Category>"
        cat_match = re.search(r"current category:\s*([A-Za-z\s]+)", prompt, re.IGNORECASE)
        if cat_match:
            detected = cat_match.group(1).strip()
            for known_cat in ["Python", "AI", "Web Development", "Data Analytics", "Machine Learning", "Automation", "Full Stack"]:
                if detected.lower().startswith(known_cat.lower()):
                    category = known_cat
                    break

        idea_catalog = {
            "Python": {
                "project_name": "DevSecOps Config Auditor",
                "category": "Python",
                "description": "High-performance CLI utility for auditing YAML/JSON configuration files, identifying CVE misconfigurations, and generating compliance scorecards.",
                "problem_statement": "Developers often deploy Kubernetes, Docker, and CI/CD manifests with insecure default privileges and exposed ports.",
                "target_users": ["DevOps Engineers", "Backend Developers", "Security Analysts"],
                "features": [
                    "Static AST and pattern analysis of Kubernetes manifests and Dockerfiles",
                    "Customizable YAML/JSON rule-engine with severity levels (LOW, MED, HIGH, CRITICAL)",
                    "Terminal dashboard with rich formatting and color-coded remediation advice",
                    "Exportable JSON and HTML compliance audit reports"
                ],
                "optional_advanced_features": [
                    "Git pre-commit hook integration",
                    "Auto-remediation patch generation"
                ],
                "technologies": ["Python", "Typer", "Pydantic", "PyYAML", "Rich", "pytest"]
            },
            "AI": {
                "project_name": "ContextPulse RAG Synthesizer",
                "category": "AI",
                "description": "Production-ready semantic RAG context engine with dynamic chunk re-ranking, token budget optimizer, and citation verification.",
                "problem_statement": "LLM applications suffer from hallucinations and lost context when ingesting large unstructured documentation sets without intelligent chunking and attribution.",
                "target_users": ["AI Engineers", "Enterprise Knowledge Workers", "Support Teams"],
                "features": [
                    "Adaptive sliding-window text chunker with overlap and metadata indexing",
                    "TF-IDF and cosine similarity hybrid retrieval scoring engine",
                    "Context synthesizer that enforces citation references and factual alignment",
                    "REST API for document ingestion, query answering, and context telemetry"
                ],
                "optional_advanced_features": [
                    "Vector store plugin interface",
                    "Confidence calibration score"
                ],
                "technologies": ["Python", "FastAPI", "Pydantic", "NumPy", "Scikit-Learn", "pytest"]
            },
            "Web Development": {
                "project_name": "MetricsForge API Gateway",
                "category": "Web Development",
                "description": "Lightweight asynchronous reverse proxy and API telemetry gateway with rate limiting, response caching, and health dashboards.",
                "problem_statement": "Microservices require unified observability and rate limiting without heavy enterprise infrastructure overhead.",
                "target_users": ["Web Developers", "API Architects", "Site Reliability Engineers"],
                "features": [
                    "Asynchronous request routing and transparent proxying",
                    "Token bucket rate limiting per API key and client IP",
                    "In-memory LRU response caching with TTL invalidation",
                    "Live metrics endpoints reporting latency percentiles (p50, p95, p99)"
                ],
                "optional_advanced_features": [
                    "Prometheus metrics exporter",
                    "Dynamic route reloading"
                ],
                "technologies": ["Python", "FastAPI", "Uvicorn", "Pydantic", "Httpx", "pytest"]
            },
            "Data Analytics": {
                "project_name": "DataPulse Anomaly Radar",
                "category": "Data Analytics",
                "description": "Time-series statistical anomaly detection and automated EDA dashboard with Z-score outlier flagging and seasonal trend decomposition.",
                "problem_statement": "Business analysts lack automated tools to spot metric drift and transaction spikes before they cause revenue loss.",
                "target_users": ["Data Analysts", "Business Intelligence Teams", "Financial Analysts"],
                "features": [
                    "Robust Z-score and Interquartile Range (IQR) outlier detection",
                    "Rolling window statistical summary and trend aggregation",
                    "Data hygiene cleaner handling missing values and categorical encoding",
                    "Interactive CLI report generator with summary distribution matrices"
                ],
                "optional_advanced_features": [
                    "Plotly interactive HTML export",
                    "Automated slack/email anomaly alerts"
                ],
                "technologies": ["Python", "Pandas", "NumPy", "Scipy", "Rich", "pytest"]
            },
            "Machine Learning": {
                "project_name": "PropensityPulse ML Engine",
                "category": "Machine Learning",
                "description": "Customer conversion propensity and churn prediction pipeline with automated feature engineering, cross-validation, and model serving.",
                "problem_statement": "E-commerce platforms need actionable lead scoring without complex multi-month ML engineering deployments.",
                "target_users": ["Data Scientists", "Growth Engineers", "Product Managers"],
                "features": [
                    "Automated feature scaling, one-hot encoding, and feature importance analysis",
                    "Random Forest and Gradient Boosted classifier ensemble training",
                    "Evaluation suite computing ROC-AUC, Precision-Recall, and F1-Score",
                    "Inference REST endpoint predicting customer conversion probabilities"
                ],
                "optional_advanced_features": [
                    "SHAP explanation generator",
                    "Model artifact versioning and rollback"
                ],
                "technologies": ["Python", "Scikit-Learn", "Pandas", "NumPy", "FastAPI", "pytest"]
            },
            "Automation": {
                "project_name": "SentinelHook Webhook Dispatcher",
                "category": "Automation",
                "description": "Fault-tolerant webhook ingestion, deduplication, and exponential backoff retry dispatcher with dead-letter queue management.",
                "problem_statement": "Third-party webhook deliveries frequently fail due to intermittent endpoint downtime and lack of automated replay mechanisms.",
                "target_users": ["Backend Engineers", "Automation Specialists", "DevOps"],
                "features": [
                    "Event queue with SHA-256 idempotency deduplication",
                    "Configurable exponential backoff retry worker with jitter",
                    "Dead-letter queue (DLQ) persistent storage for poisoned messages",
                    "Telemetry API to inspect delivery statuses and trigger manual retries"
                ],
                "optional_advanced_features": [
                    "Signature verification (HMAC-SHA256)",
                    "Rate limit pacing per target domain"
                ],
                "technologies": ["Python", "FastAPI", "SQLite", "Requests", "Pydantic", "pytest"]
            },
            "Full Stack": {
                "project_name": "TaskFlow Ops Portal",
                "category": "Full Stack",
                "description": "End-to-end incident management and task orchestration portal featuring FastAPI REST backend, SQLite persistence, and responsive interactive web UI.",
                "problem_statement": "Engineering teams require a lightweight, self-hosted operational board to manage incident response workflows and shift handovers.",
                "target_users": ["Engineering Teams", "Operations Managers", "Support Leads"],
                "features": [
                    "FastAPI REST API with full CRUD operations for tasks and incident tickets",
                    "SQLite database with normalized relational schema and state transitions",
                    "Responsive HTML5/Tailwind/JavaScript single-page frontend interface",
                    "Role-based status transitions (OPEN -> INVESTIGATING -> RESOLVED -> CLOSED)"
                ],
                "optional_advanced_features": [
                    "Audit logging of all status changes",
                    "Markdown ticket description rendering"
                ],
                "technologies": ["Python", "FastAPI", "SQLite", "Pydantic", "HTML5/JS", "pytest"]
            }
        }
        return json.dumps(idea_catalog.get(category, idea_catalog["AI"]))

    def _mock_research(self, prompt: str) -> str:
        return json.dumps({
            "feasibility": "High. The project scope is well-defined, completely self-contained, and uses robust standard libraries without complex external infrastructure dependencies.",
            "required_technologies": ["Python >= 3.10", "FastAPI", "Pydantic", "pytest"],
            "external_apis": [],
            "libraries": ["fastapi", "uvicorn", "pydantic", "pytest", "httpx"],
            "datasets": ["Synthesized realistic domain test datasets"],
            "architecture_overview": "Clean layered architecture separating core domain models, business logic controllers, API routes, and comprehensive automated test suites.",
            "implementation_challenges": [
                "Handling edge cases like malformed input payloads and concurrent requests",
                "Ensuring deterministic and reproducible test execution"
            ],
            "security_considerations": [
                "Strict Pydantic payload validation to prevent injection attacks",
                "Zero hardcoded secrets, full support for .env configuration"
            ],
            "testing_requirements": [
                "Unit test coverage for all core engine functions",
                "API integration tests using FastAPI TestClient",
                "Edge case validation for error handling and boundary values"
            ]
        })

    def _mock_architecture(self, prompt: str) -> str:
        return json.dumps({
            "folder_structure": {
                "src": ["__init__.py", "main.py", "core.py", "models.py", "api.py", "utils.py"],
                "tests": ["__init__.py", "test_core.py", "test_api.py"],
                "root": ["README.md", "requirements.txt", ".env.example", ".gitignore"]
            },
            "file_list": [
                "src/__init__.py",
                "src/models.py",
                "src/core.py",
                "src/api.py",
                "src/main.py",
                "tests/__init__.py",
                "tests/test_core.py",
                "tests/test_api.py",
                "requirements.txt",
                ".env.example",
                ".gitignore"
            ],
            "modules": [
                {"name": "models.py", "purpose": "Pydantic data schemas and domain types"},
                {"name": "core.py", "purpose": "Core business logic and processing engine"},
                {"name": "api.py", "purpose": "FastAPI routes and HTTP endpoint handlers"},
                {"name": "main.py", "purpose": "Application entrypoint and CLI runner"}
            ],
            "apis": [
                {"endpoint": "/health", "method": "GET", "description": "Service health check"},
                {"endpoint": "/process", "method": "POST", "description": "Process primary payload"},
                {"endpoint": "/metrics", "method": "GET", "description": "Retrieve operational metrics"}
            ],
            "database_schema": "SQLite in-memory or file-based relational schema if persistence required",
            "data_flow": "Client -> API Router -> Schema Validation -> Core Engine -> Response Formatter -> Client",
            "env_variables": ["APP_ENV", "PORT", "LOG_LEVEL"],
            "testing_structure": "pytest test suite with isolated fixtures and test cases"
        })

    def _mock_coding(self, prompt: str) -> str:
        files = {
            "requirements.txt": "fastapi>=0.110.0\npydantic>=2.7.0\nhttpx>=0.27.0\npytest>=8.0.0\nuvicorn>=0.29.0\n",
            ".env.example": "APP_ENV=development\nPORT=8000\nLOG_LEVEL=INFO\nAPI_KEY=your-secret-key-here\n",
            ".gitignore": "__pycache__/\n*.pyc\n.pytest_cache/\n.env\n*.db\n",
            "src/__init__.py": '"""Application package."""\n__version__ = "1.0.0"\n',
            "src/models.py": '''"""Domain data models and schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IngestionItem(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Item title or header")
    content: str = Field(..., description="Payload body content")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class ProcessRequest(BaseModel):
    query: str = Field(..., description="Search or evaluation query")
    items: List[IngestionItem] = Field(default_factory=list, description="Items to evaluate")
    top_k: int = Field(default=3, ge=1, le=20, description="Max results to return")


class MatchResult(BaseModel):
    item_id: str
    title: str
    score: float
    excerpt: str


class ProcessResponse(BaseModel):
    query: str
    matches_found: int
    results: List[MatchResult]
    latency_ms: float
''',
            "src/core.py": '''"""Core algorithmic logic and processing engine."""
import time
import re
from typing import List
from src.models import IngestionItem, MatchResult, ProcessResponse


class Engine:
    """Intelligent query matching and scoring engine."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def tokenize(self, text: str) -> set[str]:
        """Convert text into cleaned alphanumeric tokens."""
        if not self.case_sensitive:
            text = text.lower()
        tokens = re.findall(r"\\b[a-zA-Z0-9_]{2,}\\b", text)
        return set(tokens)

    def calculate_similarity(self, query_tokens: set[str], content_tokens: set[str]) -> float:
        """Compute Jaccard similarity coefficient between token sets."""
        if not query_tokens or not content_tokens:
            return 0.0
        intersection = len(query_tokens.intersection(content_tokens))
        union = len(query_tokens.union(content_tokens))
        return float(intersection) / float(union) if union > 0 else 0.0

    def process_query(self, query: str, items: List[IngestionItem], top_k: int = 3) -> ProcessResponse:
        """Evaluate query across items and rank matching results."""
        start_time = time.perf_counter()
        query_tokens = self.tokenize(query)

        scored_results: List[MatchResult] = []
        for item in items:
            content_tokens = self.tokenize(f"{item.title} {item.content} {' '.join(item.tags)}")
            score = self.calculate_similarity(query_tokens, content_tokens)

            excerpt = item.content[:120] + "..." if len(item.content) > 120 else item.content
            scored_results.append(
                MatchResult(
                    item_id=item.id,
                    title=item.title,
                    score=round(score, 4),
                    excerpt=excerpt
                )
            )

        scored_results.sort(key=lambda r: r.score, reverse=True)
        top_results = scored_results[:top_k]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return ProcessResponse(
            query=query,
            matches_found=len(top_results),
            results=top_results,
            latency_ms=elapsed_ms
        )
''',
            "src/api.py": '''"""FastAPI application endpoints."""
from fastapi import FastAPI, HTTPException
from src.models import ProcessRequest, ProcessResponse
from src.core import Engine

app = FastAPI(
    title="Daily Autonomous Project API",
    description="Production-grade API automatically engineered by Daily Project Factory",
    version="1.0.0"
)

engine = Engine()


@app.get("/health")
def health_check():
    """Service liveness and health endpoint."""
    return {"status": "healthy", "service": "DailyProjectApp", "version": "1.0.0"}


@app.post("/api/v1/process", response_model=ProcessResponse)
def process_payload(request: ProcessRequest):
    """Process incoming query against provided document items."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
    return engine.process_query(request.query, request.items, request.top_k)
''',
            "src/main.py": '''"""CLI runner and server entrypoint."""
import sys
from src.models import IngestionItem
from src.core import Engine


def run_cli_demo():
    """Run interactive demonstration in console."""
    print("========================================")
    print(" Daily Project Factory - Executable Demo")
    print("========================================")
    engine = Engine()
    sample_items = [
        IngestionItem(
            id="doc-1",
            title="FastAPI Microservices Guide",
            content="Building high-performance async microservices with Python, FastAPI, and Pydantic validation.",
            tags=["python", "fastapi", "microservices"]
        ),
        IngestionItem(
            id="doc-2",
            title="Machine Learning Pipelines",
            content="Scikit-Learn model training, hyperparameter optimization, and dataset preprocessing techniques.",
            tags=["machine-learning", "scikit-learn", "ai"]
        ),
        IngestionItem(
            id="doc-3",
            title="Automated Testing with Pytest",
            content="Writing robust unit and integration tests using pytest fixtures and coverage reports.",
            tags=["testing", "pytest", "devops"]
        )
    ]

    query = "FastAPI async testing"
    print(f"Executing query: '{query}' against {len(sample_items)} documents...")
    response = engine.process_query(query, sample_items, top_k=2)

    print(f"\\nFound {response.matches_found} matches in {response.latency_ms}ms:")
    for rank, res in enumerate(response.results, start=1):
        print(f" [{rank}] {res.title} (Score: {res.score}) -> {res.excerpt}")
    print("\\nDemo completed successfully!")


if __name__ == "__main__":
    run_cli_demo()
''',
            "tests/__init__.py": '"""Unit test package."""\n',
            "tests/test_core.py": '''"""Unit tests for the core engine."""
import pytest
from src.models import IngestionItem
from src.core import Engine


@pytest.fixture
def engine():
    return Engine()


@pytest.fixture
def sample_items():
    return [
        IngestionItem(
            id="1",
            title="Python Clean Code",
            content="Writing maintainable Python functions and classes.",
            tags=["python", "refactoring"]
        ),
        IngestionItem(
            id="2",
            title="Database Schema Design",
            content="Relational database normalization and SQL indexing.",
            tags=["database", "sql"]
        )
    ]


def test_tokenize(engine):
    tokens = engine.tokenize("Hello, World! Python_3 is awesome.")
    assert "hello" in tokens
    assert "world" in tokens
    assert "python_3" in tokens
    assert "awesome" in tokens


def test_similarity_calculation(engine):
    set1 = {"python", "fastapi", "docker"}
    set2 = {"python", "fastapi", "kubernetes"}
    score = engine.calculate_similarity(set1, set2)
    assert score == pytest.approx(0.5, 0.01)


def test_process_query(engine, sample_items):
    response = engine.process_query("Python Clean", sample_items, top_k=1)
    assert response.matches_found == 1
    assert response.results[0].item_id == "1"
    assert response.results[0].score > 0.0
    assert response.latency_ms >= 0.0
''',
            "tests/test_api.py": '''"""Integration tests for FastAPI endpoints."""
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DailyProjectApp"


def test_process_endpoint_success():
    payload = {
        "query": "microservices",
        "items": [
            {
                "id": "101",
                "title": "Cloud Architecture",
                "content": "Designing microservices for resilient cloud workloads.",
                "tags": ["cloud", "microservices"]
            }
        ],
        "top_k": 3
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "microservices"
    assert data["matches_found"] == 1
    assert data["results"][0]["item_id"] == "101"


def test_process_endpoint_empty_query():
    payload = {
        "query": "   ",
        "items": [],
        "top_k": 3
    }
    response = client.post("/api/v1/process", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
'''
        }
        return json.dumps({"files": files})

    def _mock_readme(self, prompt: str) -> str:
        return """# Project Name

[![CI/CD](https://github.com/autonomous-coder/project/actions/workflows/ci.yml/badge.svg)](https://github.com)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📌 Overview
An automated, production-grade system engineered autonomously by **Daily Project Factory**.

## 🚀 Key Features
- **High Performance**: Built with asynchronous FastAPI and optimized data structures.
- **Robust Validation**: Powered by Pydantic v2 schemas and runtime contract checking.
- **Comprehensive Testing**: 100% test pass rate with Pytest unit and integration tests.
- **Clean Architecture**: Decoupled domain models, core processing engines, and API layers.

## 🛠️ Architecture & Tech Stack
- **Language**: Python 3.10+
- **API Framework**: FastAPI / Uvicorn
- **Data Modeling**: Pydantic v2
- **Testing**: Pytest & HTTPX TestClient

## 📦 Installation & Setup
```bash
pip install -r requirements.txt
python -m src.main
```

## 🧪 Running Tests
```bash
pytest tests/ -v
```

## 📄 License
MIT License. Created autonomously by Daily Project Factory.
"""

    def _mock_debugger(self, prompt: str) -> str:
        return json.dumps({
            "analysis": "Identified syntax or assertion discrepancy in target file.",
            "root_cause": "Typo in function return type or test assertion.",
            "modified_files": {
                "src/core.py": '"""Patched core logic."""\n# Verified and repaired\n'
            }
        })

    def _mock_review(self, prompt: str) -> str:
        return json.dumps({
            "approved": True,
            "score": 9.4,
            "security_verdict": "pass",
            "strengths": [
                "Zero hardcoded secrets or API keys detected",
                "Clean modular structure with decoupled components",
                "Comprehensive unit and integration test coverage",
                "Complete, runnable code without any placeholder comments or TODOs"
            ],
            "issues": [],
            "feedback": "Outstanding implementation meeting all production standards."
        })

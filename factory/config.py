"""
Configuration and settings manager for Daily Project Factory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _clean_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve environment variable, treating empty string as None."""
    val = os.getenv(key)
    if val is not None and val.strip():
        return val.strip()
    return default


# Schedule mapping per specification
WEEKLY_SCHEDULE: Dict[str, Dict[str, str]] = {
    "Monday": {
        "category": "Python",
        "focus": "Python applications, CLI tools, utilities, algorithms, automation scripts",
        "tech_hints": ["Python", "Typer", "FastAPI", "Pydantic", "SQLite", "pytest", "Rich"],
    },
    "Tuesday": {
        "category": "AI",
        "focus": "LLM apps, RAG, AI agents, NLP, computer vision, AI utilities",
        "tech_hints": ["Python", "LangChain", "LangGraph", "FastAPI", "ChromaDB", "Pydantic", "OpenAI/Gemini"],
    },
    "Wednesday": {
        "category": "Web Development",
        "focus": "Frontend, backend, APIs, websites, dashboards",
        "tech_hints": ["FastAPI", "React", "TypeScript", "TailwindCSS", "SQLite", "Uvicorn"],
    },
    "Thursday": {
        "category": "Data Analytics",
        "focus": "Data cleaning, visualization, dashboards, SQL, statistics, EDA",
        "tech_hints": ["Python", "Pandas", "Plotly", "Streamlit", "NumPy", "DuckDB", "Matplotlib"],
    },
    "Friday": {
        "category": "Machine Learning",
        "focus": "ML models, prediction, classification, clustering, recommendation systems",
        "tech_hints": ["Python", "Scikit-Learn", "FastAPI", "Pandas", "Joblib", "Matplotlib"],
    },
    "Saturday": {
        "category": "Automation",
        "focus": "Workflow automation, scraping, APIs, productivity tools, scheduled systems",
        "tech_hints": ["Python", "BeautifulSoup4", "Requests", "APScheduler", "Rich", "Pydantic"],
    },
    "Sunday": {
        "category": "Full Stack",
        "focus": "Complete frontend + backend + database applications",
        "tech_hints": ["FastAPI", "SQLite", "SQLAlchemy", "Pydantic", "HTML5/JS", "Jinja2/React"],
    },
}

DAY_ORDER: List[str] = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]


class Settings(BaseModel):
    # LLM Settings
    llm_provider: str = Field(default_factory=lambda: _clean_env("LLM_PROVIDER", "gemini").lower())
    model_name: str = Field(default_factory=lambda: _clean_env("MODEL_NAME", "gemini-2.0-flash"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: _clean_env("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: _clean_env("OPENAI_API_KEY"))
    groq_api_key: Optional[str] = Field(default_factory=lambda: _clean_env("GROQ_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: _clean_env("ANTHROPIC_API_KEY"))

    # GitHub Settings
    github_token: Optional[str] = Field(
        default_factory=lambda: _clean_env("PAT_GITHUB_TOKEN") or _clean_env("GITHUB_TOKEN")
    )
    github_username: Optional[str] = Field(
        default_factory=lambda: _clean_env("GH_USERNAME") or _clean_env("GITHUB_USERNAME", "Aastha008")
    )
    github_organization: Optional[str] = Field(default_factory=lambda: _clean_env("GITHUB_ORGANIZATION"))
    github_default_visibility: str = Field(default_factory=lambda: _clean_env("GITHUB_DEFAULT_VISIBILITY", "public"))

    # Execution Limits & Behavior
    max_debug_attempts: int = Field(default_factory=lambda: int(_clean_env("MAX_DEBUG_ATTEMPTS", "5")))
    execution_timeout_seconds: int = Field(default_factory=lambda: int(_clean_env("EXECUTION_TIMEOUT_SECONDS", "180")))

    # Directory Paths
    base_dir: Path = Field(default=BASE_DIR)
    data_dir: Path = Field(default_factory=lambda: BASE_DIR / _clean_env("DATA_DIR", "data"))
    projects_file: Path = Field(default_factory=lambda: BASE_DIR / "data" / "projects.json")
    generated_projects_dir: Path = Field(
        default_factory=lambda: BASE_DIR / _clean_env("GENERATED_PROJECTS_DIR", "generated_projects")
    )
    logs_dir: Path = Field(default_factory=lambda: BASE_DIR / _clean_env("LOGS_DIR", "logs"))

    # Runtime Flags
    dry_run: bool = Field(default_factory=lambda: _clean_env("DRY_RUN", "false").lower() == "true")
    skip_github: bool = Field(default_factory=lambda: _clean_env("SKIP_GITHUB", "false").lower() == "true")
    mock_llm: bool = Field(default_factory=lambda: _clean_env("MOCK_LLM", "false").lower() == "true")

    def ensure_directories(self) -> None:
        """Ensure required operational directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.generated_projects_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

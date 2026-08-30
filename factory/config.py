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
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini").lower())
    model_name: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "gemini-2.5-flash"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))

    # GitHub Settings
    github_token: Optional[str] = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    github_username: Optional[str] = Field(default_factory=lambda: os.getenv("GITHUB_USERNAME", "autonomous-coder"))
    github_organization: Optional[str] = Field(default_factory=lambda: os.getenv("GITHUB_ORGANIZATION"))
    github_default_visibility: str = Field(default_factory=lambda: os.getenv("GITHUB_DEFAULT_VISIBILITY", "public"))

    # Execution Limits & Behavior
    max_debug_attempts: int = Field(default_factory=lambda: int(os.getenv("MAX_DEBUG_ATTEMPTS", "5")))
    execution_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "180")))

    # Directory Paths
    base_dir: Path = Field(default=BASE_DIR)
    data_dir: Path = Field(default_factory=lambda: BASE_DIR / os.getenv("DATA_DIR", "data"))
    projects_file: Path = Field(default_factory=lambda: BASE_DIR / "data" / "projects.json")
    generated_projects_dir: Path = Field(
        default_factory=lambda: BASE_DIR / os.getenv("GENERATED_PROJECTS_DIR", "generated_projects")
    )
    logs_dir: Path = Field(default_factory=lambda: BASE_DIR / os.getenv("LOGS_DIR", "logs"))

    # Runtime Flags
    dry_run: bool = Field(default_factory=lambda: os.getenv("DRY_RUN", "false").lower() == "true")
    skip_github: bool = Field(default_factory=lambda: os.getenv("SKIP_GITHUB", "false").lower() == "true")
    mock_llm: bool = Field(default_factory=lambda: os.getenv("MOCK_LLM", "false").lower() == "true")

    def ensure_directories(self) -> None:
        """Ensure required operational directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.generated_projects_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

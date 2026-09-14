"""
Naming utility and validation engine for Daily Project Factory.
Enforces realistic, human-readable, developer-friendly project and repository names.
"""

from __future__ import annotations

import re
from typing import List, Optional, Set, Tuple
from slugify import slugify

# Words that sound overly artificial, generic, or AI-generated
FORBIDDEN_BUZZWORDS: Set[str] = {
    "neural",
    "quantum",
    "hyper",
    "nexus",
    "smart",
    "ultra",
    "nextgen",
    "advanced",
    "intelligent",
    "dynamic",
    "revolutionary",
    "pro",
    "x",
    "engine",
    "framework",
    "matrix",
    "sentinel",
    "pulse",
    "forge",
    "radar",
    "optimizer",
    "optimization",
    "synthesizer",
    "synergy",
    "core",
    "hub",
    "turbo",
    "super",
    "mega",
    "omni",
    "automated",
    "autonomous",
    "platform",
}

# Vague or meaningless repository names
VAGUE_TERMS: Set[str] = {
    "awesome-project",
    "cool-app",
    "my-project",
    "test-project",
    "sample-app",
    "demo-app",
    "project",
    "app",
    "tool",
    "utility",
    "software",
    "daily-project",
    "new-project",
}

# Standard technical acronyms preserved in title formatting
ACRONYMS: Set[str] = {
    "api",
    "cli",
    "pdf",
    "csv",
    "sql",
    "rag",
    "json",
    "html",
    "css",
    "yaml",
    "ui",
    "url",
    "id",
    "eda",
    "ml",
    "cve",
    "qa",
}

# Meaningful natural differentiators used if a repository name is already taken
NATURAL_DIFFERENTIATORS: List[str] = [
    "simple",
    "minimal",
    "daily",
    "personal",
    "quick",
    "lite",
    "easy",
    "terminal",
    "web",
]

# Noun-to-natural-slug mapping for common single-topic projects
NATURAL_NOUN_PAIRS = {
    "expense": "expense-tracker",
    "habit": "habit-tracker",
    "study": "study-planner",
    "job": "job-tracker",
    "task": "task-manager",
    "incident": "incident-tracker",
    "resume": "resume-analyzer",
    "interview": "interview-coach",
    "pdf": "pdf-summarizer",
    "file": "file-organizer",
    "invoice": "invoice-generator",
    "quiz": "quiz-maker",
    "recipe": "recipe-finder",
    "movie": "movie-finder",
    "weather": "weather-dashboard",
    "api": "api-tester",
    "markdown": "markdown-editor",
    "password": "password-manager",
    "meeting": "meeting-notes",
    "webhook": "webhook-forwarder",
    "config": "config-auditor",
    "anomaly": "anomaly-detector",
    "churn": "churn-predictor",
}


def is_valid_repo_slug(slug: str) -> Tuple[bool, str]:
    """
    Validate whether a repository slug meets GitHub and human-friendly naming criteria.
    Returns (is_valid, reason).
    """
    if not slug or not isinstance(slug, str):
        return False, "Slug is empty or not a string"

    slug = slug.strip().lower()

    # 1. GitHub format: only lowercase alphanumeric and hyphens, no leading/trailing hyphen
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug):
        return False, "Slug must contain only lowercase alphanumeric characters and single hyphens"

    # 2. Vague names check
    if slug in VAGUE_TERMS:
        return False, f"Slug '{slug}' is too vague or generic"

    # 3. Random numbers, dates, or UUID-like suffixes check (e.g. -12345, -20260901, -a1b2c3)
    if re.search(r"-(\d{3,}|[a-f0-9]{6,}|v\d+)$", slug):
        return False, "Slug contains random numbers, version tags, or hash suffixes"

    # 4. Length check (prefer concise names)
    if len(slug) < 3:
        return False, "Slug is too short (< 3 characters)"
    if len(slug) > 35:
        return False, f"Slug is too long ({len(slug)} characters, max 35 recommended)"

    # 5. Word count check (prefer 2-4 simple words)
    words = slug.split("-")
    if len(words) > 4:
        return False, f"Slug has too many words ({len(words)} words, max 4 recommended)"

    # 6. Forbidden AI buzzwords check
    for word in words:
        if word in FORBIDDEN_BUZZWORDS:
            return False, f"Slug contains forbidden AI marketing buzzword: '{word}'"

    return True, "Valid human-readable repository slug"


def slug_to_title(slug: str) -> str:
    """
    Convert a lowercase kebab-case slug into a clean Title Case project name.
    Example: 'expense-tracker' -> 'Expense Tracker', 'pdf-chat' -> 'PDF Chat'.
    """
    words = slug.split("-")
    formatted_words = []
    for w in words:
        if w.lower() in ACRONYMS:
            formatted_words.append(w.upper())
        else:
            formatted_words.append(w.capitalize())
    return " ".join(formatted_words)


def clean_title_to_slug(title: str) -> str:
    """
    Convert a project title to a kebab-case slug, stripping forbidden buzzwords.
    """
    raw_slug = slugify(title)
    if not raw_slug:
        return "project-tool"

    words = raw_slug.split("-")

    # Filter out forbidden buzzwords and filler
    filtered = [w for w in words if w not in FORBIDDEN_BUZZWORDS and w not in {"the", "a", "an", "for", "with", "and"}]

    # Remove forced "ai-" prefix if not genuine
    if len(filtered) > 2 and filtered[0] == "ai":
        filtered.pop(0)

    if 2 <= len(filtered) <= 4:
        return "-".join(filtered)
    elif len(filtered) == 1:
        noun = filtered[0]
        return NATURAL_NOUN_PAIRS.get(noun, f"{noun}-tool")
    elif len(filtered) > 4:
        return "-".join(filtered[:3])

    return "-".join(words[:3]) if words else "project-tool"


def extract_keywords_from_text(text: str) -> List[str]:
    """Extract key descriptive words from project description or problem statement."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    tokens = clean.split()
    meaningful = [
        t for t in tokens
        if len(t) >= 3
        and t not in FORBIDDEN_BUZZWORDS
        and t not in VAGUE_TERMS
        and t not in {
            "this", "that", "with", "from", "your", "user", "users", "using", "built",
            "provides", "allows", "features", "system", "application", "simple", "helps",
            "manage", "management", "designed", "complete", "production", "ready"
        }
    ]
    return meaningful


def derive_name_from_functionality(
    project_name: str,
    description: str = "",
    problem_statement: str = "",
    category: str = "",
) -> Tuple[str, str]:
    """
    Determine the project's actual purpose and synthesize a concise,
    human-readable title and repository slug (2-4 simple words).
    """
    combined_text = f"{project_name} {description} {problem_statement}".lower()

    mapping_rules = [
        (("expense", "budget", "spending", "receipt"), "expense-tracker"),
        (("habit", "routine", "streak"), "habit-tracker"),
        (("resume", "cv", "portfolio"), "resume-analyzer"),
        (("interview", "prep", "practice", "questions"), "interview-coach"),
        (("pdf", "summariz"), "pdf-summarizer"),
        (("pdf", "chat", "ask"), "pdf-chat"),
        (("document", "summariz"), "document-summarizer"),
        (("study", "flashcard", "exam", "revision"), "study-planner"),
        (("movie", "film", "cinema", "recommend"), "movie-finder"),
        (("weather", "forecast", "climate"), "weather-dashboard"),
        (("api", "endpoint", "testing", "request"), "api-tester"),
        (("markdown", "note", "editor"), "markdown-editor"),
        (("file", "organize", "cleanup", "directory"), "file-organizer"),
        (("invoice", "billing", "receipt"), "invoice-generator"),
        (("quiz", "trivia", "flashcard"), "quiz-maker"),
        (("recipe", "meal", "cook", "food"), "recipe-finder"),
        (("meeting", "notes", "agenda", "transcript"), "meeting-notes"),
        (("password", "credential", "vault"), "password-manager"),
        (("job", "application", "hiring"), "job-tracker"),
        (("webhook", "relay", "forward", "replay"), "webhook-forwarder"),
        (("incident", "alert", "ticket", "ops"), "incident-tracker"),
        (("config", "yaml", "audit", "manifest"), "config-auditor"),
        (("rate", "limit", "throttle"), "rate-limiter"),
        (("anomaly", "outlier", "spike"), "anomaly-detector"),
        (("churn", "customer", "retention"), "churn-predictor"),
        (("url", "shortener", "link"), "link-shortener"),
    ]

    # 1. If project name contained buzzwords, check functional domain mappings first
    has_buzzword = any(b in project_name.lower() for b in FORBIDDEN_BUZZWORDS)
    if has_buzzword:
        for key_terms, target_slug in mapping_rules:
            if any(term in combined_text for term in key_terms):
                return slug_to_title(target_slug), target_slug

    # 2. Check if clean slug derived from project_name directly is valid
    candidate_slug = clean_title_to_slug(project_name)
    is_valid, _ = is_valid_repo_slug(candidate_slug)
    if is_valid:
        return slug_to_title(candidate_slug), candidate_slug

    # 3. Check functional mapping rules across text
    for key_terms, target_slug in mapping_rules:
        if any(term in combined_text for term in key_terms):
            return slug_to_title(target_slug), target_slug

    # 4. Fallback based on top extracted keywords
    keywords = extract_keywords_from_text(combined_text)
    if len(keywords) >= 2:
        slug = f"{keywords[0]}-{keywords[1]}"
        if len(keywords) >= 3 and len(slug) < 18:
            slug = f"{keywords[0]}-{keywords[1]}-{keywords[2]}"
        clean_slug = clean_title_to_slug(slug)
        is_v, _ = is_valid_repo_slug(clean_slug)
        if is_v:
            return slug_to_title(clean_slug), clean_slug

    # 5. Category-based clean default fallbacks
    category_defaults = {
        "Python": "cli-task-manager",
        "AI": "document-summarizer",
        "Web Development": "api-gateway",
        "Data Analytics": "csv-analyzer",
        "Machine Learning": "data-classifier",
        "Automation": "webhook-dispatcher",
        "Full Stack": "incident-tracker",
    }
    default_slug = category_defaults.get(category, "task-tracker")
    return slug_to_title(default_slug), default_slug


def resolve_unique_slug(
    slug: str,
    existing_slugs: Set[str],
    category: str = "",
) -> str:
    """
    Ensure repository slug does not duplicate any existing repository.
    If a duplicate is found, adds a natural meaningful differentiator
    (e.g. 'simple-expense-tracker', 'minimal-expense-tracker')
    WITHOUT appending random numbers, timestamps, or UUIDs.
    """
    clean_existing = {s.lower().strip() for s in existing_slugs if s}

    if slug not in clean_existing:
        return slug

    # Try natural developer prefixes
    for diff in NATURAL_DIFFERENTIATORS:
        candidate = f"{diff}-{slug}"
        if len(candidate.split("-")) <= 4 and len(candidate) <= 35:
            if candidate not in clean_existing:
                return candidate

    # Try natural developer suffixes
    for suffix in ["app", "cli", "web", "tool"]:
        candidate = f"{slug}-{suffix}"
        if len(candidate.split("-")) <= 4 and len(candidate) <= 35:
            if candidate not in clean_existing:
                return candidate

    return f"daily-{slug}"

# Autonomous Daily Project Factory

[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blue.svg)](https://github.com/langchain-ai/langgraph)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Testing](https://img.shields.io/badge/tested_with-pytest-yellow.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An autonomous multi-agent software engineering factory that designs, codes, tests, debugs, reviews, and publishes a brand new portfolio-quality software repository to GitHub every single day based on the day of the week.

---

## 🌟 High-Level Architecture

```
                         ┌───────────────────────┐
                         │      Scheduler        │
                         │   GitHub Actions      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Project Manager     │
                         │       Agent           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Idea Generator      │ ◄─── Inspects data/projects.json
                         │       Agent           │      (Avoids thematic repetition)
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Research / Design   │
                         │       Agent           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Architecture       │
                         │       Agent           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      Coding Agent     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      README Agent     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      Testing Agent    │
                         └───────────┬───────────┘
                                     │
                            ┌────────┴────────┐
                            │                 │
                           FAIL              PASS
                            │                 │
                            ▼                 ▼
                   ┌─────────────────┐  ┌───────────────┐
                   │ Debugger Agent  │  │ Review Agent  │
                   │ (Max 5 retries) │  └───────┬───────┘
                   └────────┬────────┘          │
                            │             PASS / FAIL
                            │ (Retry)           │
                            └───────► Testing ◄─┘ (if rejected)
                                       │ (if approved)
                                       ▼
                               ┌──────────────┐
                               │ GitHub Agent │ (Creates repo & pushes main)
                               └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │History Agent │ (Appends to data/projects.json)
                               └──────┬───────┘
                                      │
                                      ▼
                               New GitHub Repo & Report
```

---

## 📅 Weekly Project Timeline

The project category is automatically resolved from the current day of the week:

| Day | Category | Engineering Focus |
|---|---|---|
| **Monday** | `Python` | CLI tools, developer utilities, algorithms, automation scripts |
| **Tuesday** | `AI` | LLM apps, RAG context engines, AI agents, NLP, computer vision |
| **Wednesday** | `Web Development` | Frontend/backend microservices, APIs, dashboards, web portals |
| **Thursday** | `Data Analytics` | EDA pipelines, anomaly radar, visualization, SQL analytics |
| **Friday** | `Machine Learning` | Practical predictive models, classifiers, clustering, recommender systems |
| **Saturday** | `Automation` | Webhook dispatchers, scrapers, API integrations, queue schedulers |
| **Sunday** | `Full Stack` | Complete frontend + backend + database + REST API applications |

---

## 🤖 The 11 Autonomous Agents

1. **Project Manager Agent**: Resolves current date, weekday, and category matrix. Maintains state across the graph.
2. **Idea Generator Agent**: Inspects `data/projects.json` history, checks token/semantic uniqueness, and designs non-trivial portfolio ideas.
3. **Research Agent**: Assesses feasibility, selects minimal dependencies, and defines security/testing boundaries.
4. **Architecture Agent**: Designs modular directory trees, module contracts, API schemas, and dataflows.
5. **Coding Agent**: Writes complete, production-grade source code, configuration files, and test files without placeholders or TODOs.
6. **README Agent**: Generates professional GitHub documentation with installation, usage, architecture, and API guides.
7. **Testing Agent**: Executes static AST syntax checks, compilation audits, and an isolated `pytest` test suite.
8. **Debugger Agent**: Diagnoses test failures, identifies root causes, and executes surgical code repairs (up to 5 loops).
9. **Code Review Agent**: Performs static credential/secret scanning and evaluates code quality, assigning a score (0-10).
10. **GitHub Agent**: Sanitizes repo names, creates public GitHub repositories via GitHub REST API, creates initial commits, and pushes to `main`.
11. **Project History Agent**: Updates `data/projects.json` with generated project metadata and deployment status.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Git installed on your system
- (Optional) An API key for Gemini, OpenAI, or Groq (or run offline with `--mock-llm`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/daily-project-factory.git
cd daily-project-factory

# Create and activate virtual environment
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```ini
# Choose: gemini, openai, groq, or mock
LLM_PROVIDER=gemini
MODEL_NAME=gemini-2.5-flash
GEMINI_API_KEY=your_gemini_api_key

# GitHub credentials (for automated repository publishing)
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

---

## 💻 CLI Usage

### Run for Today's Scheduled Category
```bash
python run.py
```

### Force a Specific Category or Day
```bash
# Generate an AI project (Tuesday theme)
python run.py --category AI

# Generate a Full Stack project (Sunday theme)
python run.py --category "Full Stack"

# Force Thursday category
python run.py --day Thursday
```

### Run in Offline / Dry-Run Mode (Zero API Keys Needed)
```bash
# Test the complete multi-agent pipeline offline
python run.py --mock-llm --dry-run
```

### Use Specific LLM Providers
```bash
# Use OpenAI GPT-4o-mini
python run.py --provider openai --model gpt-4o-mini

# Use Groq Llama-3.3-70b
python run.py --provider groq --model llama-3.3-70b-versatile
```

---

## 🔒 Automated 24/7 GitHub Actions Setup

To enable fully autonomous daily project generation:

1. Push this repository to GitHub.
2. Go to **Settings > Secrets and variables > Actions** in your GitHub repository.
3. Add the following repository secrets:
   - `PAT_GITHUB_TOKEN`: A Personal Access Token (classic or fine-grained) with `repo` permissions to create new repositories on your behalf.
   - `GEMINI_API_KEY` (or `OPENAI_API_KEY` / `GROQ_API_KEY`): Your LLM API key.
   - `GH_USERNAME`: Your GitHub username.
4. The workflow in `.github/workflows/daily-project.yml` will automatically trigger at **06:00 UTC every day**, engineer the project, publish the new repository to your GitHub account, and commit the updated `data/projects.json` registry.

---

## 🧪 Running the Factory Test Suite

Run unit and orchestration tests for the Factory itself:
```bash
pytest tests/ -v
```

---

## 📊 Final Daily Report Example

Upon completion of each run, the system outputs the official summary:

```text
========================================
DAILY PROJECT FACTORY
========================================

Date: 2026-08-30
Day: Sunday
Category: Full Stack

Project: TaskFlow Ops Portal
Description: End-to-end incident management and task orchestration portal featuring FastAPI REST backend, SQLite persistence, and responsive interactive web UI.

Tech Stack: Python, FastAPI, SQLite, Pydantic, HTML5/JS, pytest

Agents Executed:
✓ Planner
✓ Idea Generator
✓ Researcher
✓ Architect
✓ Coder
✓ Tester
✓ Debugger
✓ Reviewer
✓ GitHub Publisher

Tests:
Passed: 5
Failed: 0

Code Review:
Score: 9.4/10

GitHub:
Repository: taskflow-ops-portal
URL: https://github.com/your-user/taskflow-ops-portal

Status: PUBLISHED
========================================
```

---

## 📄 License
MIT License. Built for autonomous software engineering innovation.

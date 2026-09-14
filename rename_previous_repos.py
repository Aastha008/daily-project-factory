"""
Batch rename utility to rename past factory-generated GitHub repositories
to simple, realistic, human-readable developer names.
"""

import os
import json
import time
import requests
from pathlib import Path

# Mapping of previous AI-generated names to simple, realistic developer names
RENAME_MAPPING = {
    "clusterbandit-ml": {
        "new_name": "recommendation-bandit",
        "title": "Recommendation Bandit",
    },
    "constraintflow-analytics": {
        "new_name": "data-cleaner",
        "title": "Data Cleaner",
    },
    "driftshield-ml": {
        "new_name": "model-drift-detector",
        "title": "Model Drift Detector",
    },
    "duckdrift-profiler": {
        "new_name": "dataset-profiler",
        "title": "Dataset Profiler",
    },
    "hookpulse-relay": {
        "new_name": "webhook-forwarder",
        "title": "Webhook Forwarder",
    },
    "loglens-ai": {
        "new_name": "log-analyzer",
        "title": "Log Analyzer",
    },
    "promptproxy-sentinel": {
        "new_name": "prompt-gateway",
        "title": "Prompt Gateway",
    },
    "queryroute-optimizer": {
        "new_name": "query-analyzer",
        "title": "Query Analyzer",
    },
    "queueforge-ops": {
        "new_name": "task-queue-monitor",
        "title": "Task Queue Monitor",
    },
    "releaserelay-engine": {
        "new_name": "dependency-tracker",
        "title": "Dependency Tracker",
    },
    "resonator-api": {
        "new_name": "api-contract-checker",
        "title": "API Contract Checker",
    },
    "schemahazard-engine": {
        "new_name": "migration-hazard-analyzer",
        "title": "Migration Hazard Analyzer",
    },
    "schemaloom-migrations": {
        "new_name": "schema-drift-detector",
        "title": "Schema Drift Detector",
    },
    "selectorshift-ops": {
        "new_name": "web-scraper-monitor",
        "title": "Web Scraper Monitor",
    },
    "shadowmesh-ops": {
        "new_name": "traffic-shadow-proxy",
        "title": "Traffic Shadow Proxy",
    },
    # Also include past records in data/projects.json
    "contextpulse-rag-synthesizer": {
        "new_name": "document-search",
        "title": "Document Search",
    },
    "taskflow-ops-portal": {
        "new_name": "incident-tracker",
        "title": "Incident Tracker",
    },
    "devsecops-config-auditor": {
        "new_name": "config-auditor",
        "title": "Config Auditor",
    },
    "api-health-sentry": {
        "new_name": "api-monitor",
        "title": "API Monitor",
    },
}


def update_projects_json(projects_file: Path) -> int:
    """Update names and repository slugs inside data/projects.json."""
    if not projects_file.exists():
        print(f"Projects file {projects_file} not found.")
        return 0

    with open(projects_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    projects = data.get("projects", [])
    for p in projects:
        old_repo = p.get("repository", "")
        if old_repo in RENAME_MAPPING:
            info = RENAME_MAPPING[old_repo]
            new_repo = info["new_name"]
            new_title = info["title"]
            print(f"[projects.json] '{old_repo}' -> '{new_repo}' ('{new_title}')")
            p["repository"] = new_repo
            p["project_name"] = new_title
            if "github_url" in p and old_repo in p["github_url"]:
                p["github_url"] = p["github_url"].replace(old_repo, new_repo)
            updated_count += 1

    with open(projects_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Updated {updated_count} records in {projects_file.name}.")
    return updated_count


def rename_github_repositories(username: str, token: str) -> None:
    """Call GitHub REST API to rename remote repositories."""
    clean_token = "".join(token.strip().split())
    clean_username = username.strip()

    headers = {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "DailyProjectFactory-Renamer",
    }

    print(f"Checking existing repositories for user '{clean_username}' on GitHub...")
    url = f"https://api.github.com/users/{clean_username}/repos?per_page=100"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:
        print(f"Failed to connect to GitHub API: {exc}")
        return

    if resp.status_code != 200:
        print(f"Error fetching user repositories: HTTP {resp.status_code} - {resp.text}")
        return

    existing_repos = {r["name"]: r for r in resp.json()}
    print(f"Found {len(existing_repos)} repositories on GitHub.")

    renamed_count = 0
    for old_name, mapping in RENAME_MAPPING.items():
        new_name = mapping["new_name"]

        if old_name in existing_repos:
            print(f"\nRenaming GitHub repository: '{old_name}' -> '{new_name}'...")
            patch_url = f"https://api.github.com/repos/{clean_username}/{old_name}"
            payload = {"name": new_name}
            try:
                patch_resp = requests.patch(patch_url, headers=headers, json=payload, timeout=20)
                if patch_resp.status_code == 200:
                    print(f"SUCCESS: Renamed to https://github.com/{clean_username}/{new_name}")
                    renamed_count += 1
                else:
                    print(f"FAILED (HTTP {patch_resp.status_code}): {patch_resp.text}")
            except Exception as e:
                print(f"Request error while renaming '{old_name}': {e}")
            time.sleep(1)  # Rate pacing
        elif new_name in existing_repos:
            print(f"Repository already named '{new_name}'. Skipping.")
        else:
            pass

    print(f"\nFinished GitHub renaming. {renamed_count} repositories renamed successfully.")


def main():
    base_dir = Path(__file__).resolve().parent
    projects_file = base_dir / "data" / "projects.json"

    # 1. Update local registry
    update_projects_json(projects_file)

    # 2. Rename on GitHub if credentials available
    raw_token = os.getenv("PAT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN") or ""
    raw_username = os.getenv("GH_USERNAME") or os.getenv("GITHUB_USERNAME") or "Aastha008"

    token = "".join(raw_token.strip().split())
    username = raw_username.strip()

    if token:
        rename_github_repositories(username, token)
    else:
        print("\nNote: No GITHUB_TOKEN or PAT_GITHUB_TOKEN found in environment.")
        print("To rename the remote repositories on GitHub, run this via the GitHub Actions workflow.")


if __name__ == "__main__":
    main()

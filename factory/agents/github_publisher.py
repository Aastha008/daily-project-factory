"""
Agent 10: GitHub Publisher Agent
Automates GitHub repository provisioning via GitHub REST API / PyGithub,
initializes local git tracking, creates initial commit, and pushes to remote.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from slugify import slugify
from factory.config import settings
from factory.state import GitHubResult, ProjectState
from factory.utils.git_tools import GitTool
from factory.utils.logger import factory_logger


class GitHubPublisherAgent:
    """GitHub Publisher creating public repositories and pushing production code."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        github_username: Optional[str] = None,
        dry_run: bool = False,
        skip_github: bool = False,
    ):
        self.github_token = github_token or settings.github_token
        self.github_username = github_username or settings.github_username
        self.dry_run = dry_run or settings.dry_run
        self.skip_github = skip_github or settings.skip_github

    def create_github_repo(
        self,
        repo_slug: str,
        description: str,
        topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create remote repository via GitHub REST API."""
        if not self.github_token:
            factory_logger.warning(
                "PAT_GITHUB_TOKEN not provided. Skipping remote GitHub repository creation.\n"
                "To enable automatic repository publishing, add PAT_GITHUB_TOKEN in GitHub Repository Secrets."
            )
            return {
                "created": False,
                "url": f"https://github.com/{self.github_username}/{repo_slug}",
                "clone_url": f"https://github.com/{self.github_username}/{repo_slug}.git",
                "error": "No token provided",
            }

        url = "https://api.github.com/user/repos"
        if settings.github_organization:
            url = f"https://api.github.com/orgs/{settings.github_organization}/repos"

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload = {
            "name": repo_slug,
            "description": description[:350],
            "private": settings.github_default_visibility.lower() == "private",
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "auto_init": False,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 201:
                data = resp.json()
                if topics:
                    clean_topics = [slugify(t) for t in topics if t][:10]
                    try:
                        requests.put(
                            f"https://api.github.com/repos/{data['owner']['login']}/{repo_slug}/topics",
                            headers=headers,
                            json={"names": clean_topics},
                            timeout=10,
                        )
                    except Exception:
                        pass
                return {
                    "created": True,
                    "url": data.get("html_url", ""),
                    "clone_url": data.get("clone_url", ""),
                }
            elif resp.status_code == 422 and "already exists" in resp.text:
                owner = settings.github_organization or self.github_username
                return {
                    "created": True,
                    "url": f"https://github.com/{owner}/{repo_slug}",
                    "clone_url": f"https://github.com/{owner}/{repo_slug}.git",
                }
            elif resp.status_code in [401, 403]:
                factory_logger.error(
                    f"GitHub API authentication failed (HTTP {resp.status_code}). "
                    "The provided token lacks repository creation permissions. "
                    "Please ensure PAT_GITHUB_TOKEN has the 'repo' scope."
                )
                owner = settings.github_organization or self.github_username
                return {
                    "created": False,
                    "url": f"https://github.com/{owner}/{repo_slug}",
                    "clone_url": f"https://github.com/{owner}/{repo_slug}.git",
                    "error": resp.text,
                }
            else:
                factory_logger.warning(f"GitHub API returned {resp.status_code}: {resp.text}")
                owner = settings.github_organization or self.github_username
                return {
                    "created": False,
                    "url": f"https://github.com/{owner}/{repo_slug}",
                    "clone_url": f"https://github.com/{owner}/{repo_slug}.git",
                    "error": resp.text,
                }
        except Exception as exc:
            factory_logger.error(f"GitHub repo creation exception: {exc}")
            owner = settings.github_organization or self.github_username
            return {
                "created": False,
                "url": f"https://github.com/{owner}/{repo_slug}",
                "clone_url": f"https://github.com/{owner}/{repo_slug}.git",
                "error": str(exc),
            }

    def publish(
        self,
        project_dir: Path,
        project_name: str,
        repo_slug: str,
        description: str,
        topics: Optional[List[str]] = None,
    ) -> GitHubResult:
        """Initialize git repo, commit, create remote, and push."""
        factory_logger.step("Creating GitHub repository")

        # 1. Local Git Init & Commit
        commit_msg = f"feat: initial implementation of {project_name}"
        GitTool.init_and_commit(
            repo_path=project_dir,
            commit_message=commit_msg,
            author_name="Daily Project Factory Bot",
            author_email="bot@dailyprojectfactory.internal",
        )

        if self.dry_run or self.skip_github or not self.github_token:
            mock_url = f"https://github.com/{self.github_username}/{repo_slug}"
            factory_logger.step("Repository published (Simulated / Local Mode)")
            factory_logger.info(f"Repository: {repo_slug}")
            factory_logger.info(f"URL: {mock_url}")
            return GitHubResult(
                repository_name=repo_slug,
                github_url=mock_url,
                status="published" if self.dry_run else "skipped",
            )

        # 2. Remote Repo Creation
        remote_info = self.create_github_repo(repo_slug, description, topics)
        if not remote_info.get("created"):
            mock_url = remote_info.get("url", f"https://github.com/{self.github_username}/{repo_slug}")
            factory_logger.warning(
                "Could not create remote repository on GitHub. "
                "Ensure PAT_GITHUB_TOKEN has the 'repo' scope in GitHub repository secrets."
            )
            return GitHubResult(
                repository_name=repo_slug,
                github_url=mock_url,
                status="skipped",
                error=remote_info.get("error"),
            )

        clone_url = remote_info.get("clone_url", "")
        repo_url = remote_info.get("url", "")

        # Inject auth token into clone_url for pushing
        auth_clone_url = clone_url
        if self.github_token and "github.com" in clone_url:
            auth_clone_url = clone_url.replace("https://", f"https://x-access-token:{self.github_token}@")

        # 3. Git Push
        pushed, push_output = GitTool.push_to_remote(project_dir, auth_clone_url, branch="main")
        if pushed:
            factory_logger.step("Repository published")
            factory_logger.info(f"Repository: {repo_slug}")
            factory_logger.info(f"URL: {repo_url}")
            return GitHubResult(
                repository_name=repo_slug,
                github_url=repo_url,
                status="published",
            )
        else:
            factory_logger.warning(f"Git push failed: {push_output}. Local repository is intact.")
            return GitHubResult(
                repository_name=repo_slug,
                github_url=repo_url,
                status="failed",
                error=push_output,
            )

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        project_name = idea.get("project_name", "Autonomous Project")
        slug = idea.get("repository_slug") or slugify(project_name)
        description = idea.get("description", "")
        topics = idea.get("technologies", [])
        project_dir = Path(state.get("project_dir", str(settings.generated_projects_dir / slug)))

        res = self.publish(project_dir, project_name, slug, description, topics)
        state["github_info"] = res.model_dump()
        state["project_status"] = res.status
        state["logs"].append(f"GitHub publishing finished with status: {res.status}")
        return state

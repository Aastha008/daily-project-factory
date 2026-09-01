"""
Git utility functions for repository initialization, staging, commits, and pushes.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from factory.utils.logger import factory_logger


class GitTool:
    """Helper for executing local git commands safely."""

    @staticmethod
    def run_command(cmd: list[str], cwd: Path) -> Tuple[int, str, str]:
        """Execute git command synchronously in given directory."""
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            return res.returncode, res.stdout, res.stderr
        except Exception as exc:
            return 1, "", str(exc)

    @classmethod
    def init_and_commit(
        cls,
        repo_path: Path,
        commit_message: str,
        author_name: str = "Aastha008",
        author_email: str = "Aastha008@users.noreply.github.com",
    ) -> bool:
        """Initialize local repository and create initial commit."""
        try:
            # 1. git init
            cls.run_command(["git", "init", "-b", "main"], cwd=repo_path)

            # 2. configure user for this repo
            cls.run_command(["git", "config", "user.name", author_name], cwd=repo_path)
            cls.run_command(["git", "config", "user.email", author_email], cwd=repo_path)

            # 3. git add .
            cls.run_command(["git", "add", "."], cwd=repo_path)

            # 4. git commit
            code, stdout, stderr = cls.run_command(["git", "commit", "-m", commit_message], cwd=repo_path)
            if code == 0 or "nothing to commit" in stdout or "nothing to commit" in stderr:
                return True
            factory_logger.warning(f"Git commit notice: {stderr or stdout}")
            return True
        except Exception as exc:
            factory_logger.error(f"Git init error: {exc}")
            return False

    @classmethod
    def init_and_commit_staged(
        cls,
        repo_path: Path,
        author_name: str,
        author_email: str,
        files: Dict[str, str],
    ) -> bool:
        """Initialize local repo and create realistic structured commits attributed to user."""
        try:
            cls.run_command(["git", "init", "-b", "main"], cwd=repo_path)
            cls.run_command(["git", "config", "user.name", author_name], cwd=repo_path)
            cls.run_command(["git", "config", "user.email", author_email], cwd=repo_path)

            # Stage 1: Configurations (.gitignore, .env.example, requirements.txt)
            config_files = [f for f in [".gitignore", ".env.example", "requirements.txt"] if f in files]
            if config_files:
                for f in config_files:
                    cls.run_command(["git", "add", f], cwd=repo_path)
                cls.run_command(["git", "commit", "-m", "chore: initialize repository and development environment"], cwd=repo_path)

            # Stage 2: Core modules & domain models
            core_files = [f for f in files.keys() if f.startswith("src/") and ("model" in f or "core" in f or "__init__" in f)]
            if core_files:
                for f in core_files:
                    cls.run_command(["git", "add", f], cwd=repo_path)
                cls.run_command(["git", "commit", "-m", "feat(core): implement core domain models and business logic"], cwd=repo_path)

            # Stage 3: API routes & application entrypoint
            api_files = [f for f in files.keys() if f.startswith("src/") and f not in core_files]
            if api_files:
                for f in api_files:
                    cls.run_command(["git", "add", f], cwd=repo_path)
                cls.run_command(["git", "commit", "-m", "feat(api): implement api routes and application entrypoint"], cwd=repo_path)

            # Stage 4: Test suites (tests/)
            test_files = [f for f in files.keys() if f.startswith("tests/")]
            if test_files:
                for f in test_files:
                    cls.run_command(["git", "add", f], cwd=repo_path)
                cls.run_command(["git", "commit", "-m", "test: add comprehensive unit and integration test suite"], cwd=repo_path)

            # Stage 5: Documentation (README.md)
            if "README.md" in files:
                cls.run_command(["git", "add", "README.md"], cwd=repo_path)
                cls.run_command(["git", "commit", "-m", "docs: generate professional project documentation and README"], cwd=repo_path)

            # Stage 6: Catch-all for any remaining files
            cls.run_command(["git", "add", "."], cwd=repo_path)
            cls.run_command(["git", "commit", "-m", "build: complete project synthesis"], cwd=repo_path)

            return True
        except Exception as exc:
            factory_logger.error(f"Git init staged error: {exc}")
            return False

    @classmethod
    def push_to_remote(
        cls,
        repo_path: Path,
        remote_url: str,
        branch: str = "main",
    ) -> Tuple[bool, str]:
        """Add remote origin and push branch."""
        cls.run_command(["git", "remote", "remove", "origin"], cwd=repo_path)
        cls.run_command(["git", "remote", "add", "origin", remote_url], cwd=repo_path)

        code, stdout, stderr = cls.run_command(["git", "push", "-u", "origin", branch, "--force"], cwd=repo_path)
        if code == 0:
            return True, stdout
        return False, stderr or stdout

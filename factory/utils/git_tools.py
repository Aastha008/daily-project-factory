"""
Git utility functions for repository initialization, staging, commits, and pushes.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
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
        author_name: str = "Daily Project Factory Bot",
        author_email: str = "bot@dailyprojectfactory.internal",
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
    def push_to_remote(
        cls,
        repo_path: Path,
        remote_url: str,
        branch: str = "main",
    ) -> Tuple[bool, str]:
        """Add remote origin and push branch."""
        # Add remote or set-url
        cls.run_command(["git", "remote", "remove", "origin"], cwd=repo_path)
        cls.run_command(["git", "remote", "add", "origin", remote_url], cwd=repo_path)

        code, stdout, stderr = cls.run_command(["git", "push", "-u", "origin", branch, "--force"], cwd=repo_path)
        if code == 0:
            return True, stdout
        return False, stderr or stdout

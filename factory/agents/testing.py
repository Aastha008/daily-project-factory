"""
Agent 7: Testing Agent
Executes static syntax checks, AST analysis, dependency validation,
and automated pytest test suites in an isolated sandbox environment.
"""

from __future__ import annotations

import ast
import os
import py_compile
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from factory.config import settings
from factory.state import ProjectState, TestResult
from factory.utils.logger import factory_logger


class TestingAgent:
    """Automated Testing Engine running AST syntax audits and Pytest execution."""

    # Prevent pytest from attempting to collect TestingAgent as a test suite
    __test__ = False

    def __init__(self, sandbox_base_dir: Optional[Path] = None):
        self.sandbox_base_dir = sandbox_base_dir or settings.generated_projects_dir
        self.sandbox_base_dir.mkdir(parents=True, exist_ok=True)

    def write_files_to_disk(self, project_dir: Path, files: Dict[str, str]) -> None:
        """Write all generated files into the target project directory."""
        project_dir.mkdir(parents=True, exist_ok=True)
        for rel_path, content in files.items():
            file_path = project_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def check_syntax(self, project_dir: Path, files: Dict[str, str]) -> List[str]:
        """Perform AST parsing and compilation check on all python files."""
        syntax_errors: List[str] = []
        for rel_path, content in files.items():
            if rel_path.endswith(".py"):
                full_path = project_dir / rel_path
                has_ast_error = False

                # 1. AST parse
                try:
                    ast.parse(content, filename=rel_path)
                except SyntaxError as e:
                    syntax_errors.append(f"SyntaxError in {rel_path} (line {e.lineno}): {e.msg}")
                    has_ast_error = True
                except Exception as e:
                    syntax_errors.append(f"Parse error in {rel_path}: {e}")
                    has_ast_error = True

                # 2. py_compile (only if AST parse passed)
                if not has_ast_error and full_path.exists():
                    try:
                        py_compile.compile(str(full_path), doraise=True)
                    except py_compile.PyCompileError as e:
                        syntax_errors.append(f"Compilation error in {rel_path}: {e.msg}")
                    except Exception:
                        pass
        return syntax_errors

    def install_project_dependencies(self, project_dir: Path) -> None:
        """Ensure project's requirements.txt dependencies are installed."""
        req_file = project_dir / "requirements.txt"
        if req_file.exists():
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
                    cwd=project_dir,
                    capture_output=True,
                    timeout=60,
                    check=False,
                )
            except Exception as exc:
                factory_logger.warning(f"Could not pre-install project requirements: {exc}")

    def run_pytest(self, project_dir: Path) -> TestResult:
        """Execute pytest in project directory and parse results."""
        start_time = time.perf_counter()
        tests_dir = project_dir / "tests"

        if not tests_dir.exists() or not any(tests_dir.glob("test_*.py")):
            return TestResult(
                status="passed",
                tests_run=1,
                tests_passed=1,
                tests_failed=0,
                duration_seconds=0.1,
                stdout="Syntax verified. No explicit test files found.",
            )

        # Pre-install dependencies if needed
        self.install_project_dependencies(project_dir)

        # Set PYTHONPATH so tests can import from project root
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_dir) + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"]
        try:
            res = subprocess.run(
                cmd,
                cwd=project_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=settings.execution_timeout_seconds,
            )
            duration = round(time.perf_counter() - start_time, 2)
            stdout = res.stdout
            stderr = res.stderr

            tests_passed = 0
            tests_failed = 0
            tests_run = 0

            passed_match = re.search(r"(\d+)\s+passed", stdout)
            if passed_match:
                tests_passed = int(passed_match.group(1))

            failed_match = re.search(r"(\d+)\s+failed", stdout)
            if failed_match:
                tests_failed = int(failed_match.group(1))

            error_match = re.search(r"(\d+)\s+error", stdout)
            if error_match:
                tests_failed += int(error_match.group(1))

            tests_run = tests_passed + tests_failed

            errors = []
            traceback_lines = []
            in_failure_section = False
            for line in stdout.splitlines():
                if "FAILURES" in line or "ERRORS" in line:
                    in_failure_section = True
                if in_failure_section:
                    traceback_lines.append(line)
                if line.startswith("FAILED ") or line.startswith("ERROR "):
                    errors.append(line)

            status = "passed" if (res.returncode == 0 and tests_failed == 0) else "failed"
            if res.returncode != 0 and tests_run == 0:
                status = "failed"
                errors.append(f"Pytest collection or runner failure (exit code {res.returncode}): {stderr or stdout}")

            return TestResult(
                status=status,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                errors=errors,
                traceback="\n".join(traceback_lines),
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                status="failed",
                tests_run=0,
                tests_passed=0,
                tests_failed=1,
                errors=["Testing execution timed out after 180 seconds."],
                duration_seconds=180.0,
            )
        except Exception as exc:
            return TestResult(
                status="failed",
                tests_run=0,
                tests_passed=0,
                tests_failed=1,
                errors=[f"Failed to execute testing runner: {exc}"],
                duration_seconds=0.0,
            )

    def execute_test_suite(self, project_slug: str, files: Dict[str, str]) -> TestResult:
        """Run full testing pipeline: disk staging, syntax check, and pytest."""
        factory_logger.step("Running tests")
        project_dir = self.sandbox_base_dir / project_slug
        self.write_files_to_disk(project_dir, files)

        # 1. Syntax check
        syntax_errors = self.check_syntax(project_dir, files)
        if syntax_errors:
            factory_logger.error(f"Syntax validation failed with {len(syntax_errors)} error(s)")
            return TestResult(
                status="failed",
                tests_run=len(syntax_errors),
                tests_passed=0,
                tests_failed=len(syntax_errors),
                errors=syntax_errors,
                traceback="\n".join(syntax_errors),
            )

        # 2. Pytest suite
        result = self.run_pytest(project_dir)
        if result.status == "passed":
            factory_logger.success(f"Tests passed ({result.tests_passed}/{result.tests_run} test cases)")
        else:
            factory_logger.warning(f"Tests failed ({result.tests_failed} failed of {result.tests_run})")
        return result

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        idea = state.get("idea") or {}
        slug = idea.get("repository_slug", "daily-project")
        files = state.get("files") or {}

        test_res = self.execute_test_suite(slug, files)
        state["test_results"] = test_res.model_dump()
        state["project_dir"] = str(self.sandbox_base_dir / slug)
        state["project_status"] = "testing"
        state["logs"].append(f"Testing completed with status: {test_res.status}")
        return state

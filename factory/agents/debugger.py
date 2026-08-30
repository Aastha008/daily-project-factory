"""
Agent 8: Debugger Agent
Analyzes execution tracebacks, syntax errors, and failed test assertions,
performing targeted surgical code repairs up to a maximum of 5 loops.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from factory.config import settings
from factory.llm.base import LLMProvider
from factory.state import ProjectState, TestResult
from factory.utils.logger import factory_logger


class DebuggerAgent:
    """Automated Debugging Specialist performing targeted repairs on broken code."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def debug_and_repair(
        self,
        files: Dict[str, str],
        test_result: Dict[str, Any],
        attempt_number: int,
    ) -> Dict[str, str]:
        """Analyze test failures and return targeted file updates."""
        factory_logger.step(f"Debugging attempt {attempt_number}/{settings.max_debug_attempts}")

        errors = test_result.get("errors", [])
        traceback = test_result.get("traceback", "")
        stdout = test_result.get("stdout", "")

        system_prompt = (
            "You are the Principal Debugger at Daily Project Factory.\n"
            "Your task is to analyze the test/syntax failure and perform SURGICAL, TARGETED fixes.\n"
            "RULES:\n"
            "1. NEVER rewrite the entire project from scratch. Only modify the specific files that caused the failure.\n"
            "2. Ensure all imports, syntax, type annotations, and logic assertions are fixed.\n"
            "3. Output MUST be valid JSON with a 'modified_files' object containing only the repaired files."
        )

        user_prompt = f"""
Debugging Attempt: {attempt_number} of {settings.max_debug_attempts}

Observed Errors:
{json.dumps(errors, indent=2)}

Pytest Traceback / Execution Log:
{traceback if traceback else stdout}

Current Project Files:
{json.dumps({k: v for k, v in files.items() if not k.endswith(('.md', '.gitignore'))}, indent=2)}

Provide your diagnosis and surgical repairs as JSON:
{{
  "analysis": "Brief diagnosis of the bug and why it occurred",
  "root_cause": "The specific function, import, or assertion that failed",
  "modified_files": {{
    "path/to/broken_file.py": "COMPLETE REPAIRED CONTENT FOR THIS SPECIFIC FILE"
  }}
}}
"""
        repair_res = self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
        )

        modified = repair_res.get("modified_files", {})
        analysis = repair_res.get("analysis", "Applied targeted bug repair.")
        factory_logger.info(f"Diagnosis: {analysis}")

        # Update files dict with modified files
        updated_files = dict(files)
        for path, content in modified.items():
            if content and isinstance(content, str):
                updated_files[path] = content
                factory_logger.info(f"Patched: {path}")

        return updated_files

    def execute_node(self, state: ProjectState) -> ProjectState:
        """LangGraph node execution."""
        current_attempts = state.get("debug_attempts", 0) + 1
        state["debug_attempts"] = current_attempts

        test_results = state.get("test_results") or {}
        files = state.get("files") or {}

        repaired_files = self.debug_and_repair(files, test_results, current_attempts)
        state["files"] = repaired_files
        state["project_status"] = "debugging"
        state["debug_history"].append({
            "attempt": current_attempts,
            "errors": test_results.get("errors", []),
        })
        state["logs"].append(f"Applied debugging repair loop {current_attempts}")
        return state

"""
Tests for TestingAgent and DebuggerAgent.
"""

import pytest
from pathlib import Path
from factory.agents.testing import TestingAgent
from factory.agents.debugger import DebuggerAgent
from factory.llm.mock_provider import MockLLMProvider


def test_testing_agent_syntax_check(tmp_path):
    """Verify testing agent detects syntax errors and parses valid code."""
    tester = TestingAgent(sandbox_base_dir=tmp_path)

    # Valid files
    valid_files = {
        "src/__init__.py": "",
        "src/app.py": "def add(a: int, b: int) -> int:\n    return a + b\n",
    }
    project_dir = tmp_path / "valid_proj"
    tester.write_files_to_disk(project_dir, valid_files)
    errors = tester.check_syntax(project_dir, valid_files)
    assert len(errors) == 0

    # Invalid syntax files
    broken_files = {
        "src/bad.py": "def broken_func(\n    return 42\n",
    }
    broken_dir = tmp_path / "bad_proj"
    tester.write_files_to_disk(broken_dir, broken_files)
    errors = tester.check_syntax(broken_dir, broken_files)
    assert len(errors) == 1
    assert "SyntaxError" in errors[0]


def test_debugger_agent_repair_loop():
    """Verify debugger agent executes repair without destroying files."""
    mock_llm = MockLLMProvider()
    debugger = DebuggerAgent(llm=mock_llm)

    files = {
        "src/core.py": "def broken():\n    return 1\n",
        "tests/test_core.py": "def test_ok():\n    assert True\n",
    }
    test_result = {
        "errors": ["AssertionError: 1 != 2"],
        "traceback": "test_core.py:2 in test_ok",
        "stdout": "FAIL",
    }

    repaired = debugger.debug_and_repair(files, test_result, attempt_number=1)
    assert "src/core.py" in repaired
    assert "tests/test_core.py" in repaired

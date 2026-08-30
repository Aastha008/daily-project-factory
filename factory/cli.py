"""
Command-line interface (CLI) for Daily Project Factory.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional
from factory.config import settings, WEEKLY_SCHEDULE
from factory.llm.factory import get_llm_provider
from factory.utils.logger import factory_logger
from factory.utils.report import generate_final_report
from factory.workflow.graph import run_project_factory

# Ensure UTF-8 console output handling across platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="daily-project-factory",
        description="Autonomous Multi-Agent AI Software Engineering Factory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                             # Run automatically for today's scheduled category
  python run.py --category AI               # Force generation of an AI project
  python run.py --category "Full Stack"     # Force generation of a Full Stack project
  python run.py --dry-run                   # Test full generation pipeline without pushing to GitHub
  python run.py --mock-llm --dry-run        # Run 100% offline with deterministic mock models
""",
    )

    parser.add_argument(
        "-c", "--category",
        type=str,
        default=None,
        help="Override project category (e.g. Python, AI, Web Development, Data Analytics, Machine Learning, Automation, Full Stack)",
    )
    parser.add_argument(
        "-d", "--day",
        type=str,
        default=None,
        help="Override day of the week (Monday, Tuesday, ...)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="LLM provider: gemini, openai, groq, mock",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (e.g. gemini-2.5-flash, gpt-4o-mini, llama-3.3-70b-versatile)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Run pipeline and test locally without creating remote GitHub repositories",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        default=False,
        help="Use built-in Mock LLM for offline deterministic verification",
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        default=False,
        help="Skip remote GitHub repository creation",
    )
    parser.add_argument(
        "--max-debug",
        type=int,
        default=5,
        help="Maximum automated debugging retry loops (default: 5)",
    )

    return parser.parse_args(args)


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI execution routine."""
    parsed = parse_args(args)

    # Apply configuration overrides
    if parsed.max_debug:
        settings.max_debug_attempts = parsed.max_debug
    if parsed.dry_run:
        settings.dry_run = True
    if parsed.mock_llm:
        settings.mock_llm = True
    if parsed.skip_github:
        settings.skip_github = True

    # Initialize LLM Provider
    llm = get_llm_provider(
        provider_name=parsed.provider,
        model_name=parsed.model,
        force_mock=parsed.mock_llm,
    )

    try:
        final_state = run_project_factory(
            llm=llm,
            override_category=parsed.category,
            override_day=parsed.day,
            dry_run=parsed.dry_run,
            skip_github=parsed.skip_github,
        )

        # Output the Official Final Daily Report Banner
        try:
            report_text = generate_final_report(final_state, use_ascii_checkmarks=False)
            factory_logger.console.print("\n" + report_text + "\n")
        except Exception:
            report_text = generate_final_report(final_state, use_ascii_checkmarks=True)
            print("\n" + report_text + "\n")

        status = final_state.get("project_status", "unknown")
        if status in ["published", "completed", "skipped"]:
            return 0
        else:
            factory_logger.error(f"Execution concluded with non-success status: {status}")
            return 1

    except Exception as exc:
        factory_logger.error(f"Fatal error during factory execution: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

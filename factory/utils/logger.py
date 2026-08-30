"""
Observability and formatted logging system for Daily Project Factory.
Produces clean timestamped output in the console and persists logs to disk.
"""

from __future__ import annotations

import datetime
import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.text import Text
from factory.config import settings


class FactoryLogger:
    """Rich timestamped logger for observability."""

    def __init__(self, logs_dir: Optional[Path] = None):
        self.console = Console()
        self.logs_dir = logs_dir or settings.logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.logs_dir / f"daily_factory_{datetime.date.today().isoformat()}.log"
        self._setup_file_handler()

    def _setup_file_handler(self) -> None:
        self.file_logger = logging.getLogger("DailyProjectFactoryFile")
        self.file_logger.setLevel(logging.INFO)
        if not self.file_logger.handlers:
            fh = logging.FileHandler(self.current_log_file, encoding="utf-8")
            formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
            fh.setFormatter(formatter)
            self.file_logger.addHandler(fh)

    @staticmethod
    def _get_time_str() -> str:
        return datetime.datetime.now().strftime("%H:%M")

    def step(self, message: str, style: str = "bold cyan") -> None:
        """Log standard agent milestone step."""
        time_str = self._get_time_str()
        log_line = f"[{time_str}] {message}"
        self.console.print(f"[{time_str}] [bold cyan]{message}[/bold cyan]")
        self.file_logger.info(message)

    def info(self, message: str) -> None:
        """Log informational message."""
        time_str = self._get_time_str()
        self.console.print(f"[{time_str}] [white]{message}[/white]")
        self.file_logger.info(message)

    def success(self, message: str) -> None:
        """Log success message."""
        time_str = self._get_time_str()
        self.console.print(f"[{time_str}] [bold green]{message}[/bold green]")
        self.file_logger.info(f"SUCCESS: {message}")

    def warning(self, message: str) -> None:
        """Log warning message."""
        time_str = self._get_time_str()
        self.console.print(f"[{time_str}] [bold yellow]{message}[/bold yellow]")
        self.file_logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        time_str = self._get_time_str()
        self.console.print(f"[{time_str}] [bold red]{message}[/bold red]")
        self.file_logger.error(message)


# Global singleton instance
factory_logger = FactoryLogger()

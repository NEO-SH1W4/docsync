"""File system monitoring module."""

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    """Configuration for file monitoring."""

    paths: list[Path]
    patterns: list[str] = None
    ignore_patterns: list[str] = None

    def __post_init__(self):
        """Convert string paths to Path objects and set defaults."""
        self.paths = [Path(p) if isinstance(p, str) else p for p in self.paths]
        self.patterns = self.patterns or [
            "*.txt",
            "*.md",
        ]  # Default patterns from tests
        self.ignore_patterns = self.ignore_patterns or [
            "*.tmp",
        ]  # Default ignore pattern


class FileMonitor(FileSystemEventHandler):
    """Monitor file system changes with thread-safe tracking."""

    def __init__(self, config: MonitorConfig) -> None:
        """Initialize the monitor with given configuration."""
        super().__init__()
        self.config = config
        self.observer = Observer()
        self._modified_files: set[Path] = set()
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start monitoring the configured paths."""
        try:
            for path in self.config.paths:
                if not path.exists():
                    logger.warning(f"Path does not exist: {path}")
                    continue
                self.observer.schedule(self, str(path), recursive=True)
            self.observer.start()
            logger.info(f"Started monitoring paths: {self.config.paths}")
        except Exception as e:
            logger.exception(f"Failed to start monitoring: {e}")
            raise

    def stop(self) -> None:
        """Stop monitoring and clean up resources."""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped monitoring")
        except Exception as e:
            logger.exception(f"Error stopping monitor: {e}")
            raise

    def _should_process_file(self, path: Path) -> bool:
        """Check if a file should be processed based on patterns."""
        # Check ignore patterns first
        if any(path.match(pattern) for pattern in self.config.ignore_patterns):
            logger.debug(f"Ignoring file: {path}")
            return False

        # Then check include patterns
        return any(path.match(pattern) for pattern in self.config.patterns)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            path = Path(event.src_path)
            if self._should_process_file(path):
                with self._lock:
                    self._modified_files.add(path)
                    logger.debug(f"File modified: {path}")

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            path = Path(event.src_path)
            if self._should_process_file(path):
                with self._lock:
                    self._modified_files.add(path)
                    logger.debug(f"File created: {path}")

    def get_modified_files(self) -> set[Path]:
        """Get and clear the set of modified files."""
        with self._lock:
            modified = self._modified_files.copy()
            self._modified_files.clear()
            return modified


def create_monitor(
    paths: list[str],
    patterns: Optional[list[str]] = None,
    ignore_patterns: Optional[list[str]] = None,
) -> FileMonitor:
    """Create and configure a FileMonitor instance.

    Args:
        paths: List of paths to monitor
        patterns: List of file patterns to include (default: ["*.txt", "*.md"])
        ignore_patterns: List of file patterns to ignore (default: ["*.tmp"])

    Returns:
        Configured FileMonitor instance
    """
    config = MonitorConfig(
        paths=paths,
        patterns=patterns,
        ignore_patterns=ignore_patterns,
    )
    return FileMonitor(config)

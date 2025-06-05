"""Tests for the file system monitoring module."""

import os
import tempfile
from pathlib import Path
from time import sleep
from typing import Generator

import pytest
from watchdog.observers import Observer

from src.monitor import FileMonitor, MonitorConfig, create_monitor

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def monitor(temp_dir: Path) -> Generator[FileMonitor, None, None]:
    """Create a FileMonitor instance for testing."""
    config = MonitorConfig(
        paths=[temp_dir],
        patterns=["*.txt", "*.md"],
        ignore_patterns=["*.tmp"]
    )
    monitor = FileMonitor(config)
    monitor.start()
    yield monitor
    monitor.stop()

def test_monitor_creation(temp_dir: Path) -> None:
    """Test that monitor is created correctly."""
    monitor = create_monitor([str(temp_dir)])
    assert isinstance(monitor, FileMonitor)
    assert isinstance(monitor.observer, Observer)
    
def test_file_creation_detection(monitor: FileMonitor, temp_dir: Path) -> None:
    """Test that file creation is detected."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    sleep(1)  # Allow time for event processing
    
    modified = monitor.get_modified_files()
    assert test_file in modified

def test_file_modification_detection(monitor: FileMonitor, temp_dir: Path) -> None:
    """Test that file modification is detected."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("initial content")
    sleep(1)
    
    modified = monitor.get_modified_files()  # Clear initial creation event
    
    test_file.write_text("modified content")
    sleep(1)
    
    modified = monitor.get_modified_files()
    assert test_file in modified

def test_ignore_patterns(monitor: FileMonitor, temp_dir: Path) -> None:
    """Test that ignored files are not detected."""
    test_file = temp_dir / "test.tmp"
    test_file.write_text("ignored content")
    sleep(1)
    
    modified = monitor.get_modified_files()
    assert not modified  # Should be empty since .tmp files are ignored

def test_multiple_modifications(monitor: FileMonitor, temp_dir: Path) -> None:
    """Test handling of multiple modifications."""
    files = [
        temp_dir / "test1.txt",
        temp_dir / "test2.txt",
        temp_dir / "test3.md"
    ]
    
    for file in files:
        file.write_text("test content")
    sleep(1)
    
    modified = monitor.get_modified_files()
    assert len(modified) == len(files)
    assert all(f in modified for f in files)

def test_repeated_modifications(monitor: FileMonitor, temp_dir: Path) -> None:
    """Test that rapid repeated modifications are handled correctly."""
    test_file = temp_dir / "test.txt"
    
    # Multiple rapid modifications
    for i in range(5):
        test_file.write_text(f"content {i}")
    sleep(1)
    
    modified = monitor.get_modified_files()
    assert test_file in modified
    assert len(modified) == 1  # Should only register as one modification

def test_monitor_cleanup(temp_dir: Path) -> None:
    """Test that monitor cleanup works correctly."""
    monitor = create_monitor([str(temp_dir)])
    monitor.start()
    monitor.stop()
    
    assert not monitor.observer.is_alive()


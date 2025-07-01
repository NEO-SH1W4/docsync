from pathlib import Path

import pytest

from docsync import DocSync


def test_docsync_initialization():
    sync = DocSync()
    assert sync.config == {}


def test_docsync_with_config():
    config_path = Path("tests/fixtures/test_config.yaml")
    sync = DocSync(config_path)
    assert sync.config_path == config_path

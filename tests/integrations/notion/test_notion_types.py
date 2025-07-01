# test_notion_types.py
from datetime import datetime

import pytest

from docsync.integrations.notion.types import NotionDatabase, NotionPage


def test_notion_page_creation():
    page = NotionPage(
        id="test_id",
        title="Test Page",
        content="# Test Content",
        last_edited=datetime.now(),
        metadata={"key": "value"},
        parent_id="parent_id",
    )

    assert page.id == "test_id"
    assert page.title == "Test Page"
    assert page.content == "# Test Content"
    assert isinstance(page.last_edited, datetime)
    assert page.metadata == {"key": "value"}
    assert page.parent_id == "parent_id"


def test_notion_database_creation():
    db = NotionDatabase(
        id="test_db",
        title="Test Database",
        description="Test Description",
        schema={"field": {"type": "text"}},
        pages=[],
        last_synced=datetime.now(),
    )

    assert db.id == "test_db"
    assert db.title == "Test Database"
    assert db.description == "Test Description"
    assert db.schema == {"field": {"type": "text"}}
    assert isinstance(db.pages, list)
    assert isinstance(db.last_synced, datetime)

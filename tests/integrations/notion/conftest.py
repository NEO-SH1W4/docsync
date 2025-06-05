# conftest.py
import pytest
import asyncio
from pathlib import Path
from datetime import datetime

from docsync.integrations.notion import (
    NotionConfig,
    NotionMapping,
    NotionPage,
    NotionDatabase
)

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_notion_page():
    return NotionPage(
        id='test_page_id',
        title='Test Page',
        content='# Test Content\nThis is a test page.',
        last_edited=datetime.now(),
        metadata={
            'tags': ['test', 'documentation'],
            'status': 'draft'
        }
    )

@pytest.fixture
def sample_notion_database():
    return NotionDatabase(
        id='test_db_id',
        title='Test Database',
        description='A test database',
        schema={
            'Name': {'type': 'title'},
            'Status': {'type': 'select'},
            'Tags': {'type': 'multi_select'}
        },
        pages=[],
        last_synced=datetime.now()
    )

@pytest.fixture
def temp_docs_structure(tmp_path):
    # Criar estrutura de diretórios e arquivos de teste
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()
    
    # Criar alguns arquivos de teste
    (docs_dir / 'test1.md').write_text('# Test Document 1')
    (docs_dir / 'test2.md').write_text('# Test Document 2')
    
    # Criar subdiretório com mais arquivos
    api_dir = docs_dir / 'api'
    api_dir.mkdir()
    (api_dir / 'api.md').write_text('# API Documentation')
    
    return docs_dir

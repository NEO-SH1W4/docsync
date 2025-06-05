# test_notion_integration.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path

from docsync.integrations.notion import (
    NotionBridge,
    NotionClient,
    NotionConfig,
    NotionMapping,
    NotionPage,
    NotionDatabase
)

@pytest.fixture
def notion_config():
    return NotionConfig(
        token='test_token',
        workspace_id='test_workspace',
        mappings=[
            NotionMapping(
                source_path=Path('./docs'),
                target_id='test_page_id'
            )
        ]
    )

@pytest.fixture
def mock_client():
    with patch('docsync.integrations.notion.client.NotionClient') as mock:
        client = mock.return_value
        client.verify_connection.return_value = True
        yield client

@pytest.fixture
def notion_bridge(notion_config, mock_client):
    return NotionBridge(config=notion_config)

@pytest.mark.asyncio
async def test_notion_bridge_initialization(notion_bridge):
    await notion_bridge.initialize()
    assert notion_bridge.client is not None
    assert notion_bridge.config is not None

@pytest.mark.asyncio
async def test_notion_client_connection(mock_client, notion_config):
    client = NotionClient(notion_config)
    assert await client.verify_connection() == True

@pytest.mark.asyncio
async def test_notion_page_retrieval(mock_client, notion_config):
    client = NotionClient(notion_config)
    mock_client.get_page.return_value = {
        'id': 'test_id',
        'title': [{'plain_text': 'Test Page'}],
        'last_edited_time': '2025-06-04T12:00:00Z'
    }
    
    page = await client.get_page('test_id')
    assert page['id'] == 'test_id'
    assert page['title'][0]['plain_text'] == 'Test Page'

@pytest.mark.asyncio
async def test_notion_database_retrieval(mock_client, notion_config):
    client = NotionClient(notion_config)
    mock_client.get_database.return_value = NotionDatabase(
        id='test_db',
        title='Test Database',
        description='Test Description',
        schema={},
        pages=[]
    )
    
    db = await client.get_database('test_db')
    assert isinstance(db, NotionDatabase)
    assert db.id == 'test_db'
    assert db.title == 'Test Database'

@pytest.mark.asyncio
async def test_sync_mapping(notion_bridge, tmp_path):
    # Criar estrutura de teste
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()
    test_file = docs_dir / 'test.md'
    test_file.write_text('# Test Document')
    
    # Configurar mapping
    mapping = NotionMapping(
        source_path=docs_dir,
        target_id='test_target'
    )
    
    # Testar sincronização
    await notion_bridge._sync_mapping(mapping)
    # Aqui adicionaremos mais verificações quando implementarmos
    # a lógica completa de sincronização

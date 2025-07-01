"""
DOCSYNC Notion Tests Configuration
================================

Configuração e fixtures comuns para testes do módulo Notion.
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Configuração de logging para testes
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configuração do pytest-asyncio
pytest_plugins = ("pytest_asyncio",)

# Dados de teste
TEST_DATA = {
    "page": {
        "id": "test_page_id",
        "object": "page",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "parent": {"type": "database_id", "database_id": "test_db_id"},
        "properties": {"title": {"title": [{"text": {"content": "Test Page"}}]}},
    },
    "database": {
        "id": "test_db_id",
        "object": "database",
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": "2025-01-01T00:00:00.000Z",
        "title": [{"text": {"content": "Test Database"}}],
        "properties": {"title": {"type": "title", "title": {}}},
    },
    "block": {
        "id": "test_block_id",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": "Test content"}}]},
    },
}


@pytest.fixture
def test_data():
    """Retorna dados de teste padrão"""
    return TEST_DATA


@pytest.fixture
def mock_api_response():
    """Mock padrão para respostas da API"""

    def _make_response(status=200, data=None, rate_limit=100):
        mock = Mock()
        mock.status = status
        mock.headers = {
            "x-ratelimit-remaining": str(rate_limit),
            "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 3600),
            "retry-after": "60",
        }
        mock.json = AsyncMock(return_value=data or {"object": "page", "id": "test_id"})
        return mock

    return _make_response


@pytest.fixture
def temp_workspace(tmp_path):
    """Cria workspace temporário para testes"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()

    # Criar estrutura básica
    docs = workspace / "docs"
    docs.mkdir()

    # Criar alguns arquivos de teste
    (docs / "test1.md").write_text("# Test 1\nContent 1")
    (docs / "test2.md").write_text("# Test 2\nContent 2")

    yield workspace

    # Cleanup
    shutil.rmtree(workspace)


@pytest.fixture
def test_config(temp_workspace):
    """Configuração padrão para testes"""
    from docsync.integrations.notion import NotionConfig, NotionMapping

    return NotionConfig(
        token="test_token",
        workspace_id="test_workspace",
        mappings=[
            NotionMapping(source_path=temp_workspace / "docs", target_id="test_page_id")
        ],
    )


@pytest.fixture
def file_helper(temp_workspace):
    """Helper para manipulação de arquivos de teste"""

    class FileHelper:
        def create_file(self, name: str, content: str) -> Path:
            path = temp_workspace / "docs" / name
            path.write_text(content)
            return path

        def read_file(self, name: str) -> str:
            path = temp_workspace / "docs" / name
            return path.read_text()

        def delete_file(self, name: str):
            path = temp_workspace / "docs" / name
            path.unlink()

    return FileHelper()


@pytest.fixture
def mock_http_session():
    """Mock para sessão HTTP"""

    class MockSession:
        def __init__(self):
            self.responses = {}
            self.calls = []

        def add_response(
            self, method: str, url: str, response: dict, status: int = 200
        ):
            key = f"{method}:{url}"
            self.responses[key] = (status, response)

        async def request(self, method: str, url: str, **kwargs):
            key = f"{method}:{url}"
            self.calls.append((method, url, kwargs))

            status, response = self.responses.get(key, (200, {"id": "test_id"}))
            return self.mock_response(status, response)

        def mock_response(self, status: int, data: dict):
            mock = Mock()
            mock.status = status
            mock.headers = {
                "x-ratelimit-remaining": "100",
                "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 3600),
            }
            mock.json = AsyncMock(return_value=data)
            return mock

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    return MockSession()


def pytest_configure(config):
    """Configuração global do pytest"""
    config.addinivalue_line("markers", "integration: mark test as integration test")

    # Configurar cobertura de código
    config.option.cov_source = ["docsync"]
    config.option.cov_report = "term-missing"


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup automático para cada teste"""
    # Backup de variáveis de ambiente
    old_env = dict(os.environ)

    # Configurar ambiente de teste
    os.environ.update(
        {
            "NOTION_TOKEN": "test_token",
            "NOTION_WORKSPACE": "test_workspace",
            "DOCSYNC_ENV": "test",
        }
    )

    yield

    # Restaurar ambiente
    os.environ.clear()
    os.environ.update(old_env)

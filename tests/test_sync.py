"""
Testes para o sistema de sincronização GUARDRIVE.

Implementa testes automatizados para validar a funcionalidade
do sistema de sincronização, incluindo:
- Carregamento de configuração
- Sincronização de arquivos
- Manipulação de documentos
- Controle de versão
- Mapeamento de caminhos
- Tratamento de erros

Author: DocSync Team
Date: 2025-06-03
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.docsync.config import Config, DocumentType, load_config
from src.docsync.sync_manager import (
    DocumentHandler,
    SyncManager,
    VersionController,
)


# Fixtures para configuração de teste
@pytest.fixture
def test_config():
    """Configuração base para testes."""
    return {
        "templates_dir": "templates",
        "output_dir": "output",
        "backup_dir": "backups",
        "temp_dir": "temp",
        "log_level": "DEBUG",
        "esg": {
            "metrics_enabled": True,
            "custom_templates": {},
            "output_format": "markdown",
            "validation_level": "strict",
        },
        "sync": {
            "watch_paths": [],
            "ignore_patterns": [".git", "*.tmp"],
            "auto_sync": True,
            "sync_interval": 300,
            "real_time_sync": False,
        },
        "guardrive": {
            "enabled": True,
            "base_path": "/test/guardrive",
            "docs_path": "GUARDRIVE_DOCS",
            "dev_path": "AREA_DEV",
            "path_mappings": [
                {
                    "source_path": "GUARDRIVE_DOCS/technical",
                    "target_path": "AREA_DEV/dev_docs",
                    "doc_type": "technical",
                    "bidirectional": True,
                },
            ],
            "doc_handlers": {
                "markdown": {"file_extensions": ["md"], "preserve_metadata": True},
            },
            "version_control": {"enabled": True, "provider": "git"},
        },
    }


@pytest.fixture
def temp_test_dir():
    """Cria diretório temporário para testes."""
    test_dir = tempfile.mkdtemp()
    yield Path(test_dir)
    shutil.rmtree(test_dir)


@pytest.fixture
def mock_file_system():
    """Mock para operações de sistema de arquivos."""
    with patch("aiofiles.os") as mock_os, patch("aiofiles.open") as mock_open:
        yield mock_os, mock_open


@pytest.fixture
def sync_manager(test_config):
    """Cria instância do SyncManager para testes."""
    config = Config(**test_config)
    return SyncManager(config)


# Testes de Configuração
class TestConfiguration:
    """Testes para carregamento e validação de configuração."""

    def test_load_valid_config(self, test_config, temp_test_dir):
        """Testa carregamento de configuração válida."""
        config_path = temp_test_dir / "test_config.yaml"
        with open(config_path, "w") as f:
            import yaml

            yaml.dump(test_config, f)

        config = load_config(config_path)
        assert config["guardrive"]["enabled"] is True
        assert config["guardrive"]["base_path"] == "/test/guardrive"

    def test_invalid_config_structure(self):
        """Testa validação de estrutura inválida."""
        with pytest.raises(ValueError):
            Config(invalid="config")

    def test_path_mapping_validation(self, test_config):
        """Testa validação de mapeamentos de caminho."""
        config = Config(**test_config)
        mapping = config.guardrive.path_mappings[0]
        assert mapping.doc_type == DocumentType.TECHNICAL
        assert mapping.bidirectional is True


# Testes de Sincronização
@pytest.mark.asyncio
class TestSynchronization:
    """Testes para funcionalidade de sincronização."""

    async def test_file_sync(self, sync_manager, mock_file_system, temp_test_dir):
        """Testa sincronização básica de arquivo."""
        mock_os, mock_open = mock_file_system

        # Configura mocks
        source_file = temp_test_dir / "test.md"
        target_file = temp_test_dir / "sync" / "test.md"

        # Simula arquivo fonte
        mock_open.return_value.__aenter__.return_value.read.return_value = (
            b"test content"
        )

        # Executa sincronização
        await sync_manager.handle_file_change(source_file)

        # Verifica chamadas
        mock_os.copy.assert_awaited_with(source_file, target_file)

    async def test_ignore_patterns(self, sync_manager, temp_test_dir):
        """Testa padrões de ignorar arquivos."""
        temp_file = temp_test_dir / "test.tmp"
        assert sync_manager._should_ignore(temp_file) is True


# Testes de Manipulação de Documentos
@pytest.mark.asyncio
class TestDocumentHandler:
    """Testes para manipulação de documentos."""

    async def test_markdown_handler(self, test_config):
        """Testa manipulação de arquivos markdown."""
        handler_config = test_config["guardrive"]["doc_handlers"]["markdown"]
        handler = DocumentHandler(handler_config)

        assert handler._is_supported_file(Path("test.md")) is True
        assert handler._is_supported_file(Path("test.txt")) is False

    async def test_metadata_preservation(self, mock_file_system):
        """Testa preservação de metadados."""
        handler = DocumentHandler(
            {"file_extensions": ["md"], "preserve_metadata": True},
        )

        metadata = await handler._extract_metadata(Path("test.md"))
        assert isinstance(metadata, dict)


# Testes de Controle de Versão
@pytest.mark.asyncio
class TestVersionControl:
    """Testes para controle de versão."""

    async def test_git_integration(self, temp_test_dir):
        """Testa integração com Git."""
        vc = VersionController({"enabled": True, "provider": "git"})

        with patch("aiogit.Repository") as mock_repo:
            await vc.initialize_repo(temp_test_dir)
            mock_repo.create.assert_awaited_with(temp_test_dir)

    async def test_backup_creation(self, temp_test_dir):
        """Testa criação de backup."""
        vc = VersionController({"enabled": True, "backup_enabled": True})

        test_file = temp_test_dir / "test.md"
        with patch("aiofiles.os.copy") as mock_copy:
            success = await vc.create_backup(test_file)
            assert success is True
            mock_copy.assert_awaited_once()


# Testes de Tratamento de Erros
@pytest.mark.asyncio
class TestErrorHandling:
    """Testes para cenários de erro."""

    async def test_sync_failure_recovery(self, sync_manager, mock_file_system):
        """Testa recuperação de falha de sincronização."""
        mock_os, _ = mock_file_system
        mock_os.copy.side_effect = OSError("Test error")

        with pytest.raises(Exception):
            await sync_manager.sync_all()

    async def test_invalid_path_handling(self, sync_manager):
        """Testa manipulação de caminhos inválidos."""
        invalid_path = Path("/invalid/path")
        assert sync_manager._find_mapping_for_file(invalid_path) is None


# Testes de Integração
@pytest.mark.asyncio
class TestIntegration:
    """Testes de integração do sistema."""

    async def test_full_sync_cycle(self, sync_manager, temp_test_dir):
        """Testa ciclo completo de sincronização."""
        # Prepara estrutura de teste
        docs_dir = temp_test_dir / "GUARDRIVE_DOCS"
        dev_dir = temp_test_dir / "AREA_DEV"
        docs_dir.mkdir(parents=True)
        dev_dir.mkdir(parents=True)

        # Cria arquivo de teste
        test_file = docs_dir / "test.md"
        test_file.write_text("Test content")

        # Executa sincronização
        with patch.object(sync_manager, "_sync_directory_pair"):
            await sync_manager.sync_all()
            sync_manager._sync_directory_pair.assert_awaited()

    async def test_real_time_monitoring(self, sync_manager):
        """Testa monitoramento em tempo real."""
        with patch.object(sync_manager.monitor, "start") as mock_start:
            sync_manager.sync_config.real_time_sync = True
            await sync_manager.start()
            mock_start.assert_called_once()

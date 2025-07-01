"""
DOCSYNC Notion Bridge
====================

Interface de alto nível para sincronização entre sistema de arquivos local
e Notion, gerenciando estados, cache e operações atômicas.

Classes
-------
NotionBridge: Interface principal de sincronização
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from ...core.base import DocSyncError
from ...core.sync import SyncManager
from .client import NotionClient
from .config import NotionConfig, NotionMapping

logger = logging.getLogger(__name__)


class NotionBridge:
    """Ponte principal para integração com Notion."""

    def __init__(
        self, config: NotionConfig, sync_manager: Optional[SyncManager] = None
    ):
        self.config = config
        self.client = NotionClient(config)
        self.sync_manager = sync_manager
        self.cache: Dict[str, Dict] = {}
        self._sync_lock = asyncio.Lock()

    async def initialize(self):
        """Inicializa conexão e estruturas necessárias."""
        logger.info("Inicializando ponte com Notion...")
        try:
            # Verificar conexão
            if not await self.client.verify_connection():
                raise DocSyncError("Não foi possível conectar ao Notion")

            # Mapear estruturas
            for mapping in self.config.mappings:
                await self._setup_mapping(mapping)

            logger.info("Ponte com Notion inicializada com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar ponte com Notion: {e}")
            raise

    async def _setup_mapping(self, mapping: NotionMapping):
        """Configura mapeamento entre sistema de arquivos e Notion."""
        try:
            # Verificar existência da página/database no Notion
            target = await self.client.get_page(mapping.target_id)

            # Verificar estrutura local
            if not mapping.source_path.exists():
                mapping.source_path.mkdir(parents=True)

            # Criar/atualizar índice de sincronização
            await self._update_sync_index(mapping)

            logger.info(
                f'Mapeamento configurado: {mapping.source_path} -> {target["title"]}'
            )

        except Exception as e:
            logger.error(f"Erro ao configurar mapeamento {mapping.source_path}: {e}")
            raise

    async def _update_sync_index(self, mapping: NotionMapping):
        """Atualiza índice de sincronização para um mapeamento."""
        index_file = mapping.source_path / ".notion_sync"

        try:
            if index_file.exists():
                data = json.loads(index_file.read_text())
            else:
                data = {"files": {}, "last_sync": None}

            # Atualizar índice com arquivos locais
            for file in mapping.source_path.glob("**/*.md"):
                if file.name.startswith("."):
                    continue

                rel_path = str(file.relative_to(mapping.source_path))
                content = file.read_text()
                file_hash = hashlib.sha256(content.encode()).hexdigest()

                data["files"][rel_path] = {
                    "hash": file_hash,
                    "last_modified": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat(),
                    "notion_id": data["files"].get(rel_path, {}).get("notion_id"),
                }

            # Salvar índice atualizado
            index_file.write_text(json.dumps(data, indent=2))

        except Exception as e:
            logger.error(f"Erro ao atualizar índice de sincronização: {e}")
            raise

    async def sync(self):
        """Realiza sincronização bidirecional."""
        async with self._sync_lock:
            logger.info("Iniciando sincronização com Notion...")

            try:
                for mapping in self.config.mappings:
                    await self._sync_mapping(mapping)

            except Exception as e:
                logger.error(f"Erro durante sincronização: {e}")
                raise

    async def _sync_mapping(self, mapping: NotionMapping):
        """Sincroniza um mapeamento específico."""
        logger.info(f"Sincronizando mapeamento: {mapping.source_path}")

        try:
            # Carregar índice de sincronização
            index_file = mapping.source_path / ".notion_sync"
            if not index_file.exists():
                await self._update_sync_index(mapping)

            sync_data = json.loads(index_file.read_text())

            # Sincronizar alterações locais para Notion
            await self._sync_local_changes(mapping, sync_data)

            # Sincronizar alterações do Notion para local
            await self._sync_notion_changes(mapping, sync_data)

            # Atualizar timestamp de última sincronização
            sync_data["last_sync"] = datetime.now().isoformat()
            index_file.write_text(json.dumps(sync_data, indent=2))

        except Exception as e:
            logger.error(f"Erro ao sincronizar mapeamento {mapping.source_path}: {e}")
            raise

    async def _sync_local_changes(self, mapping: NotionMapping, sync_data: Dict):
        """Sincroniza alterações locais para o Notion."""
        for file in mapping.source_path.glob("**/*.md"):
            if file.name.startswith("."):
                continue

            rel_path = str(file.relative_to(mapping.source_path))
            content = file.read_text()
            current_hash = hashlib.sha256(content.encode()).hexdigest()

            file_data = sync_data["files"].get(rel_path, {})
            stored_hash = file_data.get("hash")

            if current_hash != stored_hash:
                # Arquivo foi modificado localmente
                notion_id = file_data.get("notion_id")
                if notion_id:
                    # Atualizar página existente no Notion
                    await self._update_notion_page(notion_id, file, current_hash)
                else:
                    # Criar nova página no Notion
                    notion_id = await self._create_notion_page(mapping.target_id, file)

                sync_data["files"][rel_path] = {
                    "hash": current_hash,
                    "last_modified": datetime.now().isoformat(),
                    "notion_id": notion_id,
                }

    async def _sync_notion_changes(self, mapping: NotionMapping, sync_data: Dict):
        """Sincroniza alterações do Notion para local."""
        # Obter todas as páginas do database/página alvo
        pages = await self.client.get_pages_in_database(mapping.target_id)

        for page in pages:
            # Encontrar arquivo local correspondente
            local_path = None
            notion_id = page["id"]

            for rel_path, file_data in sync_data["files"].items():
                if file_data.get("notion_id") == notion_id:
                    local_path = mapping.source_path / rel_path
                    break

            if not local_path:
                # Criar novo arquivo local
                title = page["properties"]["Name"]["title"][0]["plain_text"]
                local_path = mapping.source_path / f"{title}.md"

            # Verificar se conteúdo do Notion é mais recente
            notion_updated = datetime.fromisoformat(
                page["last_edited_time"].replace("Z", "+00:00")
            )
            local_updated = datetime.fromisoformat(
                sync_data["files"]
                .get(str(local_path.relative_to(mapping.source_path)), {})
                .get("last_modified", "1970-01-01")
            )

            if notion_updated > local_updated:
                # Atualizar arquivo local
                content = await self._convert_notion_to_markdown(page)
                local_path.write_text(content)

                rel_path = str(local_path.relative_to(mapping.source_path))
                sync_data["files"][rel_path] = {
                    "hash": hashlib.sha256(content.encode()).hexdigest(),
                    "last_modified": notion_updated.isoformat(),
                    "notion_id": notion_id,
                }

    async def _create_notion_page(self, parent_id: str, file: Path) -> str:
        """Cria uma nova página no Notion."""
        content = file.read_text()
        title = file.stem

        # Criar página
        page = await self.client.create_page(
            parent_id=parent_id, title=title, content=content
        )

        return page["id"]

    async def _update_notion_page(self, page_id: str, file: Path, content_hash: str):
        """Atualiza uma página existente no Notion."""
        content = file.read_text()

        await self.client.update_page(page_id=page_id, content=content)

    async def _convert_notion_to_markdown(self, page: Dict) -> str:
        """Converte conteúdo do Notion para Markdown."""
        # TODO: Implementar conversão completa
        title = page["properties"]["Name"]["title"][0]["plain_text"]
        return f"# {title}\n\n"  # Placeholder

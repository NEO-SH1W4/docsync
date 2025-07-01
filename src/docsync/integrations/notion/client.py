"""
DOCSYNC Notion Client
====================

Cliente HTTP assíncrono para API do Notion com suporte a:
- Rate limiting
- Retry automático
- Cache de respostas
- Tratamento de erros
- Conversão de tipos
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import aiohttp
from cachetools import TTLCache

from .config import NotionConfig
from .types import (
    API_VERSION,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CACHE_TTL,
    MARKDOWN_BLOCK_MARKERS,
    BlockType,
    NotionAuthError,
    NotionBlock,
    NotionDatabase,
    NotionError,
    NotionObjectType,
    NotionPage,
    NotionRateLimitError,
)

logger = logging.getLogger(__name__)


class NotionClient:
    """Cliente HTTP assíncrono para API do Notion"""

    def __init__(self, config: NotionConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limits = {"remaining": 100, "reset_at": datetime.now()}
        self._cache = TTLCache(maxsize=1000, ttl=DEFAULT_CACHE_TTL)
        self._retry_locks: Dict[str, asyncio.Lock] = {}

    async def initialize(self):
        """Inicializa cliente e sessão HTTP"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(
                connect=self.config.timeout["connect"],
                total=self.config.timeout["read"] + self.config.timeout["write"],
            )
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.token}",
                    "Notion-Version": API_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=timeout,
                raise_for_status=True,
            )

    async def close(self):
        """Fecha sessão e libera recursos"""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Realiza requisição à API com retry e cache"""
        if not self._session:
            await self.initialize()

        url = urljoin(self.config.base_url, endpoint)
        cache_key = self._get_cache_key(method, url, data)

        # Verificar cache
        if use_cache and method == "GET":
            cached = self._cache.get(cache_key)
            if cached:
                return cached

        # Obter/criar lock para retry
        if cache_key not in self._retry_locks:
            self._retry_locks[cache_key] = asyncio.Lock()

        async with self._retry_locks[cache_key]:
            retries = 0
            last_error = None

            while retries <= self.config.max_retries:
                try:
                    # Verificar rate limit
                    if self._rate_limits["remaining"] <= 0:
                        wait_time = (
                            self._rate_limits["reset_at"] - datetime.now()
                        ).total_seconds()
                        if wait_time > 0:
                            await asyncio.sleep(wait_time)

                    async with self._session.request(
                        method=method, url=url, json=data, params=params
                    ) as response:
                        result = await self._handle_response(response)

                        # Atualizar cache
                        if use_cache and method == "GET":
                            self._cache[cache_key] = result

                        return result

                except NotionRateLimitError as e:
                    last_error = e
                    if retries == self.config.max_retries:
                        raise
                    await asyncio.sleep(e.retry_after)

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_error = e
                    if retries == self.config.max_retries:
                        raise NotionError(f"Erro de conexão: {str(e)}")
                    await asyncio.sleep(self.config.retry_delay * (2**retries))

                retries += 1

            raise last_error or NotionError("Erro desconhecido após tentativas")

    async def _handle_response(
        self, response: aiohttp.ClientResponse
    ) -> Dict[str, Any]:
        """Processa resposta da API"""
        # Atualizar rate limits
        self._rate_limits["remaining"] = int(
            response.headers.get("x-ratelimit-remaining", 100)
        )
        reset_at = int(response.headers.get("x-ratelimit-reset", 0))
        self._rate_limits["reset_at"] = datetime.fromtimestamp(reset_at)

        data = await response.json()

        if response.status == 200:
            return data

        if response.status == 401:
            raise NotionAuthError("Token inválido ou expirado")

        if response.status == 429:
            retry_after = int(response.headers.get("retry-after", 60))
            raise NotionRateLimitError(retry_after)

        raise NotionError(
            data.get("message", "Erro desconhecido"), str(response.status)
        )

    def _get_cache_key(self, method: str, url: str, data: Optional[Dict] = None) -> str:
        """Gera chave de cache para requisição"""
        key = f"{method}:{url}"
        if data:
            key += f":{hashlib.sha256(json.dumps(data).encode()).hexdigest()}"
        return key

    async def _convert_to_notion_page(self, data: Dict[str, Any]) -> NotionPage:
        """Converte resposta da API em objeto NotionPage"""
        blocks = []
        if data.get("has_children"):
            block_data = await self._request("GET", f"blocks/{data['id']}/children")
            blocks = [
                NotionBlock.from_dict(block) for block in block_data.get("results", [])
            ]

        return NotionPage(
            id=data["id"],
            type=NotionObjectType.PAGE,
            created_time=datetime.fromisoformat(
                data["created_time"].replace("Z", "+00:00")
            ),
            last_edited_time=datetime.fromisoformat(
                data["last_edited_time"].replace("Z", "+00:00")
            ),
            title=(
                data["properties"]["title"]["title"][0]["plain_text"]
                if data.get("properties", {}).get("title")
                else ""
            ),
            parent=data["parent"],
            properties=data.get("properties", {}),
            blocks=blocks,
            created_by=data.get("created_by"),
            last_edited_by=data.get("last_edited_by"),
            archived=data.get("archived", False),
        )

    async def _convert_to_notion_database(self, data: Dict[str, Any]) -> NotionDatabase:
        """Converte resposta da API em objeto NotionDatabase"""
        pages = await self.get_pages_in_database(data["id"])

        return NotionDatabase(
            id=data["id"],
            type=NotionObjectType.DATABASE,
            created_time=datetime.fromisoformat(
                data["created_time"].replace("Z", "+00:00")
            ),
            last_edited_time=datetime.fromisoformat(
                data["last_edited_time"].replace("Z", "+00:00")
            ),
            title=data["title"][0]["plain_text"] if data.get("title") else "",
            description=data.get("description", ""),
            properties=data["properties"],
            pages=pages,
            created_by=data.get("created_by"),
            last_edited_by=data.get("last_edited_by"),
            archived=data.get("archived", False),
        )

    def _format_block(self, block_type: BlockType, content: str) -> Dict[str, Any]:
        """Formata um bloco para a API do Notion"""
        return {
            "object": "block",
            "type": block_type.value,
            block_type.value: {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            },
        }

    def _convert_markdown_to_blocks(self, markdown: str) -> List[Dict[str, Any]]:
        """Converte Markdown para blocos do Notion"""
        blocks = []
        current_block = None
        lines = markdown.split("\n")
        code_language = "plain"

        for line in lines:
            if not line.strip():
                if current_block:
                    blocks.append(current_block)
                    current_block = None
                continue

            # Verificar marcadores
            block_type = None
            content = line.strip()

            # Tratar blocos de código
            if line.startswith("```"):
                if current_block and current_block["type"] == "code":
                    # Fechando bloco de código
                    blocks.append(current_block)
                    current_block = None
                    continue
                else:
                    # Iniciando bloco de código
                    code_language = content[3:] or "plain"
                    current_block = {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "language": code_language,
                            "rich_text": [{"type": "text", "text": {"content": ""}}],
                        },
                    }
                    continue

            # Se estiver dentro de um bloco de código
            if current_block and current_block["type"] == "code":
                current_block["code"]["rich_text"][0]["text"]["content"] += line + "\n"
                continue

            # Verificar outros marcadores
            for marker, btype in MARKDOWN_BLOCK_MARKERS.items():
                if line.startswith(marker):
                    block_type = btype
                    content = line[len(marker) :].strip()
                    break

            # Se não encontrou marcador específico, é parágrafo
            if block_type is None:
                block_type = BlockType.PARAGRAPH

            # Criar bloco baseado no tipo
            blocks.append(self._format_block(block_type, content))

        # Adicionar último bloco se existir
        if current_block:
            blocks.append(current_block)

        return blocks

    async def _delete_blocks(self, blocks: List[Union[NotionBlock, str]]) -> None:
        """Deleta blocos do Notion"""
        for block in blocks:
            block_id = block.id if isinstance(block, NotionBlock) else block
            await self._request("DELETE", f"blocks/{block_id}")

    async def _append_blocks(self, page_id: str, blocks: List[Dict[str, Any]]) -> None:
        """Adiciona blocos a uma página"""
        await self._request(
            "PATCH", f"blocks/{page_id}/children", data={"children": blocks}
        )

    async def verify_connection(self) -> bool:
        """Verifica conexão com API"""
        try:
            await self._request("GET", "users/me")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            return False

    async def get_page(self, page_id: str) -> NotionPage:
        """Obtém uma página do Notion"""
        data = await self._request("GET", f"pages/{page_id}")
        return await self._convert_to_notion_page(data)

    async def get_page_content(self, page_id: str) -> List[NotionBlock]:
        """Obtém conteúdo de uma página"""
        data = await self._request("GET", f"blocks/{page_id}/children")
        return [NotionBlock.from_dict(block) for block in data.get("results", [])]

    async def get_database(self, database_id: str) -> NotionDatabase:
        """Obtém um banco de dados do Notion"""
        data = await self._request("GET", f"databases/{database_id}")
        return await self._convert_to_notion_database(data)

    async def get_pages_in_database(self, database_id: str) -> List[NotionPage]:
        """Obtém todas as páginas em um banco de dados"""
        pages = []
        has_more = True
        start_cursor = None

        while has_more:
            query_data = {
                "page_size": DEFAULT_BATCH_SIZE,
                "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
            }
            if start_cursor:
                query_data["start_cursor"] = start_cursor

            results = await self._request(
                "POST", f"databases/{database_id}/query", data=query_data
            )

            for page in results["results"]:
                pages.append(await self._convert_to_notion_page(page))

            has_more = results.get("has_more", False)
            start_cursor = results.get("next_cursor")

        return pages

    async def create_page(self, parent_id: str, title: str, content: str) -> NotionPage:
        """Cria uma nova página no Notion"""
        # Determinar tipo de parent (page ou database)
        parent_type = "page_id" if len(parent_id) == 36 else "database_id"

        page_data = {
            "parent": {parent_type: parent_id},
            "properties": {
                "title" if parent_type == "page_id" else "Name": {
                    "title": [{"text": {"content": title}}]
                }
            },
        }

        if content:
            page_data["children"] = self._convert_markdown_to_blocks(content)

        data = await self._request("POST", "pages", data=page_data)
        return await self._convert_to_notion_page(data)

    async def update_page(
        self, page_id: str, content: str = None, properties: Dict = None
    ) -> NotionPage:
        """Atualiza uma página existente"""
        if properties:
            await self._request(
                "PATCH", f"pages/{page_id}", data={"properties": properties}
            )

        if content is not None:
            blocks = self._convert_markdown_to_blocks(content)
            # Primeiro limpar blocos existentes
            existing = await self.get_page_content(page_id)
            await self._delete_blocks(existing)
            # Adicionar novos blocos
            await self._append_blocks(page_id, blocks)

        return await self.get_page(page_id)

    async def search_pages(
        self,
        query: str,
        page_size: int = DEFAULT_BATCH_SIZE,
        filter_property: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> List[NotionPage]:
        """Pesquisa páginas no Notion"""
        search_data = {
            "query": query,
            "page_size": page_size,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }

        if filter_property:
            search_data["filter"] = {"property": filter_property}
        if sort_by:
            search_data["sort"] = {"property": sort_by, "direction": "ascending"}

        data = await self._request("POST", "search", data=search_data)
        pages = []

        for page_data in data.get("results", []):
            if page_data["object"] == "page":
                pages.append(await self._convert_to_notion_page(page_data))

        return pages

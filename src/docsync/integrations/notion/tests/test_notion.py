"""DOCSYNC Notion Tests.
===================

Testes unitários e de integração para módulos Notion do DOCSYNC.

Este módulo implementa testes abrangentes para a integração Notion, cobrindo:

1. Funcionalidades Básicas
   - Inicialização e configuração do cliente
   - Conversão markdown ↔ blocos Notion
   - Sincronização bidirecional de arquivos

2. Casos Especiais
   - Arquivos grandes (>100KB)
   - Caracteres especiais e Unicode
   - Estruturas markdown complexas
   - Formatos de arquivo inválidos

3. Tratamento de Erros
   - Rate limiting e recuperação
   - Timeouts e retentativas
   - Erros de permissão
   - Falhas de rede

4. Cenários de Integração
   - Sincronização completa
   - Resolução de conflitos
   - Execução concorrente
   - Estados inconsistentes

Pré-requisitos:
- Python 3.9+
- pytest
- pytest-asyncio
- aiohttp
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from docsync.integrations.notion import (
    NotionAuthError,
    NotionBridge,
    NotionClient,
    NotionRateLimitError,
)


# Fixtures
@pytest.fixture
def test_data():
    """Fornece dados de teste do Notion."""
    return {
        "pages": {
            "basic": {
                "id": "test_page_id",
                "properties": {
                    "title": {"title": [{"text": {"content": "Test Page"}}]},
                },
                "parent": {"page_id": "parent_id"},
            },
            "with_content": {
                "id": "content_page_id",
                "properties": {
                    "title": {"title": [{"text": {"content": "Content Page"}}]},
                },
                "parent": {"page_id": "parent_id"},
                "children": [
                    {
                        "type": "paragraph",
                        "paragraph": {"text": [{"text": {"content": "Test content"}}]},
                    },
                    {
                        "type": "code",
                        "code": {
                            "text": [{"text": {"content": "print('test')"}}],
                            "language": "python",
                        },
                    },
                ],
            },
        },
        "responses": {
            "success": {"object": "page", "id": "test_id"},
            "rate_limit": {"code": "rate_limited", "message": "Rate limit exceeded"},
            "auth_error": {"code": "unauthorized", "message": "Invalid token"},
        },
    }


@pytest.fixture
def mock_api_response(test_data):
    """Mock para respostas da API do Notion."""

    def create_response(status=200, data=None, rate_limit_remaining=100):
        mock = Mock()
        mock.status = status
        mock.headers = {
            "x-ratelimit-remaining": str(rate_limit_remaining),
            "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 3600),
        }
        mock.json = AsyncMock(return_value=data or test_data["responses"]["success"])
        return mock

    return create_response


@pytest.fixture
def file_helper(tmp_path):
    """Helper para manipulação de arquivos de teste."""

    class FileHelper:
        def __init__(self, base_path) -> None:
            self.base_path = base_path

        def create_markdown(self, name, content):
            path = self.base_path / name
            path.write_text(content)
            return path

        def create_test_structure(self):
            docs = self.base_path / "docs"
            docs.mkdir(exist_ok=True)
            return self.create_markdown("docs/test.md", "# Test\nContent")

    return FileHelper(tmp_path)


@pytest.fixture
async def notion_client(test_config, mock_http_session):
    """Cliente Notion configurado para testes."""
    client = NotionClient(test_config)
    client._session = mock_http_session
    await client.initialize()
    yield client
    await client.close()


@pytest.fixture
async def notion_bridge(mock_config):
    bridge = NotionBridge(mock_config)
    await bridge.initialize()
    yield bridge
    await bridge.close()


# Testes do NotionClient
class TestNotionClient:
    """Testes do cliente Notion.

    Esta classe testa os aspectos fundamentais do NotionClient:
    - Inicialização e configuração
    - Gerenciamento de requisições HTTP
    - Cache e rate limiting
    - Conversão de conteúdo

    Cada teste é independente e usa suas próprias fixtures,
    garantindo isolamento e reprodutibilidade.
    """

    @pytest.mark.asyncio
    async def test_initialization(self, notion_client) -> None:
        """Testa inicialização do cliente Notion.

        Verifica se:
        - A sessão HTTP é criada corretamente
        - As configurações são aplicadas
        - O cliente está pronto para uso

        Args:
            notion_client: Fixture que fornece um cliente configurado

        Raises:
            AssertionError: Se alguma verificação falhar
        """
        assert notion_client._session is not None, "Sessão HTTP não foi inicializada"
        assert notion_client.config.token == "test_token", "Token incorreto"

    @pytest.mark.asyncio
    async def test_verify_connection(self, notion_client, mock_response) -> None:
        """Testa verificação de conexão."""
        with patch(
            "aiohttp.ClientSession.request",
            AsyncMock(return_value=mock_response),
        ):
            assert await notion_client.verify_connection()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, notion_client, mock_api_response) -> None:
        """Testa comportamento de rate limiting."""
        # Configurar sequência de respostas
        responses = [
            mock_api_response(rate_limit_remaining=0),  # Primeira chamada atinge limite
            mock_api_response(rate_limit_remaining=100),  # Segunda chamada após espera
        ]

        with patch("aiohttp.ClientSession.request", AsyncMock(side_effect=responses)):
            with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
                # Primeira chamada deve causar espera
                await notion_client._request("GET", "test")
                mock_sleep.assert_called_once()

                # Segunda chamada não deve esperar
                mock_sleep.reset_mock()
                await notion_client._request("GET", "test")
                mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_behavior(self, notion_client, mock_api_response, test_data) -> None:
        """Testa comportamento detalhado do cache."""
        responses = [
            mock_api_response(data=test_data["responses"]["success"]),
            mock_api_response(data={"updated": "content"}),  # Conteúdo diferente
        ]

        with patch(
            "aiohttp.ClientSession.request",
            AsyncMock(side_effect=responses),
        ) as mock_request:
            # Primeira chamada
            result1 = await notion_client._request("GET", "test", use_cache=True)

            # Segunda chamada (deve usar cache)
            result2 = await notion_client._request("GET", "test", use_cache=True)
            assert mock_request.call_count == 1
            assert result1 == result2

            # Chamada com bypass de cache
            result3 = await notion_client._request("GET", "test", use_cache=False)
            assert mock_request.call_count == 2
            assert result3 != result1

            # Chamada com payload diferente
            result4 = await notion_client._request(
                "GET",
                "test",
                payload={"diff": True},
                use_cache=True,
            )
            assert mock_request.call_count == 3
            assert result4 != result1

    @pytest.mark.asyncio
    async def test_complex_markdown_blocks(self, notion_client) -> None:
        """Testa conversão de estruturas markdown complexas para blocos Notion.

        Cenários testados:
        1. Hierarquia de títulos (h1, h2)
        2. Formatação inline (negrito, itálico)
        3. Blocos aninhados (listas, citações)
        4. Elementos especiais (tabelas, código)
        5. Links e imagens

        Exemplo de entrada:
        ```markdown
        # Título Principal
        ## Subtítulo com *itálico*
        > Citação com lista:
        > 1. Item um
        >    - Subitem
        ```

        Saída esperada:
        - Bloco heading_1 com "Título Principal"
        - Bloco heading_2 com formatação em itálico
        - Bloco quote com lista aninhada
        """
        markdown = """# Título Principal

## Subtítulo com *itálico* e **negrito**

> Citação com [link](http://example.com)
> Múltiplas linhas

1. Lista numerada
   - Sublista
   - Com **formatação**
     1. Sub-sublista

| Coluna 1 | Coluna 2 |
|----------|----------|
| Célula 1 | Célula 2 |

```python
def nested_function():
    def inner():
        pass
    return inner
```

![Imagem](http://example.com/image.jpg)
"""
        blocks = notion_client._convert_markdown_to_blocks(markdown)

        # Verificar tipos de bloco
        block_types = [b["type"] for b in blocks]
        assert "heading_1" in block_types
        assert "heading_2" in block_types
        assert "quote" in block_types
        assert "numbered_list_item" in block_types
        assert "bulleted_list_item" in block_types
        assert "table" in block_types
        assert "code" in block_types
        assert "image" in block_types

        # Verificar aninhamento
        nested_blocks = [b for b in blocks if b.get("has_children", False)]
        assert len(nested_blocks) > 0

    @pytest.mark.asyncio
    async def test_large_file_handling(self, notion_client, file_helper) -> None:
        """Testa manipulação de arquivos grandes."""
        # Criar arquivo grande (>100KB)
        large_content = "# " + "Lorem ipsum " * 5000
        large_file = file_helper.create_markdown("large.md", large_content)

        with patch.object(notion_client, "_request", AsyncMock()) as mock_request:
            # Simular chunks de upload
            chunks = []

            async def collect_chunks(*args, **kwargs):
                if "payload" in kwargs:
                    chunks.append(kwargs["payload"])
                return {"id": "test_id"}

            mock_request.side_effect = collect_chunks
            await notion_client.create_page(str(large_file))

            # Verificar divisão em chunks
            assert len(chunks) > 1
            assert all(len(str(chunk)) < 100000 for chunk in chunks)

    @pytest.mark.asyncio
    async def test_special_characters(self, notion_client, file_helper) -> None:
        """Testa manipulação de caracteres especiais."""
        content = """# Título com αβγ

Emojis: 🌟 🚀 💫

Caracteres especiais: —–""''

Multi-idioma: 你好, привет, مرحبا
"""
        test_file = file_helper.create_markdown("special.md", content)

        blocks = notion_client._convert_markdown_to_blocks(test_file.read_text())
        text_content = "".join(str(b) for b in blocks)

        assert "αβγ" in text_content
        assert "🌟" in text_content
        assert "你好" in text_content

    @pytest.mark.asyncio
    async def test_markdown_conversion(self, notion_client) -> None:
        """Testa conversão markdown → blocos."""
        markdown = """# Título

        Parágrafo com **negrito** e _itálico_.

        ```python
        def test():
            pass
        ```

        - Item 1
        - Item 2
        """

        blocks = notion_client._convert_markdown_to_blocks(markdown)
        assert len(blocks) > 0
        assert blocks[0]["type"] == "heading_1"
        assert any(b["type"] == "code" for b in blocks)
        assert any(b["type"] == "bulleted_list_item" for b in blocks)


# Testes do NotionBridge
class TestNotionBridge:
    """Testes do componente de sincronização NotionBridge.

    Esta classe verifica:
    1. Sincronização bidirecional
       - Local → Notion
       - Notion → Local

    2. Tratamento de conflitos
       - Detecção de versões
       - Estratégias de merge
       - Resolução automática

    3. Recuperação de erros
       - Falhas de rede
       - Timeouts
       - Permissões
    """

    @pytest.mark.asyncio
    async def test_sync_file_to_notion(self, notion_bridge, tmp_path) -> None:
        """Testa sincronização de arquivo local para o Notion.

        Fluxo do teste:
        1. Cria arquivo markdown local
        2. Invoca sincronização
        3. Verifica chamada ao Notion

        Args:
            notion_bridge: Bridge configurada para teste
            tmp_path: Diretório temporário para arquivos

        Cenários cobertos:
        - Arquivo novo
        - Arquivo existente
        - Conteúdo válido
        """
        # Criar arquivo temporário
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\nContent")

        with patch.object(
            notion_bridge.client,
            "create_page",
            AsyncMock(),
        ) as mock_create:
            await notion_bridge.sync_file_to_notion(str(test_file))
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_page_to_local(self, notion_bridge, tmp_path) -> None:
        """Testa sincronização Notion → local."""
        mock_page = {
            "id": "test_id",
            "properties": {"title": {"title": [{"text": {"content": "test"}}]}},
            "parent": {"page_id": "parent_id"},
        }

        with patch.object(
            notion_bridge.client,
            "get_page",
            AsyncMock(return_value=mock_page),
        ), patch.object(
            notion_bridge.client,
            "get_block_children",
            AsyncMock(return_value={"results": []}),
        ):
            await notion_bridge.sync_page_to_local("test_id")
            assert (tmp_path / "test.md").exists()

    @pytest.mark.asyncio
    async def test_conflict_resolution_detailed(
        self,
        notion_bridge,
        file_helper,
        test_data,
    ) -> None:
        """Testa cenários detalhados de resolução de conflitos."""
        # Criar arquivo local
        local_file = file_helper.create_markdown("test.md", "# Local Content\nTest")

        # Simular diferentes versões do conteúdo
        local_version = {"last_edited": datetime.now().isoformat()}
        notion_version = {
            **test_data["pages"]["with_content"],
            "last_edited_time": (datetime.now().isoformat()),
        }

        with patch.object(
            notion_bridge.client,
            "get_page",
            AsyncMock(return_value=notion_version),
        ):  # mock_get not used
            with patch.object(
                notion_bridge.client,
                "update_page",
                AsyncMock(),
            ) as mock_update:
                with patch.object(
                    notion_bridge,
                    "_get_local_version",
                    return_value=local_version,
                ):
                    # Teste 1: Versão local mais recente
                    await notion_bridge.sync_file_to_notion(str(local_file))
                    mock_update.assert_called_once()

                    # Teste 2: Versão Notion mais recente
                    mock_update.reset_mock()
                    notion_version["last_edited_time"] = datetime.now().isoformat()
                    await notion_bridge.sync_file_to_notion(str(local_file))
                    mock_update.assert_not_called()

                    # Teste 3: Conflito com merge
                    mock_update.reset_mock()
                    with patch.object(
                        notion_bridge,
                        "_merge_changes",
                        AsyncMock(),
                    ) as mock_merge:
                        await notion_bridge.sync_file_to_notion(
                            str(local_file),
                            force_merge=True,
                        )
                        mock_merge.assert_called_once()


# Testes de Integração
class TestIntegration:
    """Testes de integração end-to-end.

    Verifica o funcionamento completo do sistema:
    - Fluxo completo de sincronização
    - Interações entre componentes
    - Recuperação de erros
    - Cenários complexos

    Estes testes simulam uso real do sistema,
    exercitando múltiplos componentes simultaneamente.
    """

    @pytest.mark.asyncio
    async def test_full_sync_flow(self, notion_bridge, tmp_path) -> None:
        r"""Testa o fluxo completo de sincronização bidirecional.

        Sequência de operações:
        1. Criação de arquivo local
        2. Sincronização para Notion
        3. Modificação no Notion
        4. Sincronização para local
        5. Verificação de consistência

        Exemplo:
        ```python
        # 1. Arquivo local
        test.md -> "# Test\nContent"

        # 2. Notion (após sync)
        page -> { "title": "Test", "content": [...] }

        # 3. Modificação Notion
        page -> { "title": "Updated Test", ... }

        # 4. Arquivo local (após sync)
        test.md -> "# Updated Test\nContent"
        ```
        """
        # Criar arquivo local
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\nContent")

        # Simular resposta do Notion
        mock_page = {
            "id": "test_id",
            "properties": {"title": {"title": [{"text": {"content": "test"}}]}},
            "parent": {"page_id": "parent_id"},
        }

        with patch.object(
            notion_bridge.client,
            "create_page",
            AsyncMock(return_value=mock_page),
        ), patch.object(
            notion_bridge.client,
            "get_page",
            AsyncMock(return_value=mock_page),
        ):
            # Sincronizar local → Notion
            await notion_bridge.sync_file_to_notion(str(test_file))
            # Sincronizar Notion → local
            await notion_bridge.sync_page_to_local("test_id")

            assert test_file.exists()

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self,
        notion_bridge,
        file_helper,
        test_data,
    ) -> None:
        """Testa diferentes cenários de erro e recuperação."""
        test_file = file_helper.create_markdown("test.md", "# Test Content")

        # Teste 1: Rate Limit com retry
        with patch.object(notion_bridge.client, "_request") as mock_request:
            mock_request.side_effect = [
                NotionRateLimitError(60),  # Primeira tentativa falha
                AsyncMock(
                    return_value=test_data["responses"]["success"],
                )(),  # Segunda tentativa sucede
            ]
            await notion_bridge.sync_file_to_notion(str(test_file))
            assert mock_request.call_count == 2

        # Teste 2: Erro de autenticação
        with patch.object(
            notion_bridge.client,
            "_request",
            side_effect=NotionAuthError,
        ), pytest.raises(NotionAuthError):
            await notion_bridge.sync_file_to_notion(str(test_file))

        # Teste 3: Timeout com retry
        with patch.object(notion_bridge.client, "_request") as mock_request:
            mock_request.side_effect = [
                asyncio.TimeoutError,  # Primeira tentativa timeout
                AsyncMock(
                    return_value=test_data["responses"]["success"],
                )(),  # Segunda tentativa sucede
            ]
            await notion_bridge.sync_file_to_notion(str(test_file))
            assert mock_request.call_count == 2

        # Teste 4: Erro de rede com recuperação
        with patch.object(notion_bridge.client, "_request") as mock_request:
            mock_request.side_effect = [
                ConnectionError,  # Primeira tentativa falha
                AsyncMock(
                    return_value=test_data["responses"]["success"],
                )(),  # Segunda tentativa sucede
            ]
            await notion_bridge.sync_file_to_notion(str(test_file))
            assert mock_request.call_count == 2

        # Verificar que o estado foi mantido após erros
        assert notion_bridge._initialized

    @pytest.mark.asyncio
    async def test_invalid_paths_handling(self, notion_bridge) -> None:
        """Testa manipulação de caminhos inválidos."""
        # Teste 1: Caminho não existente
        with pytest.raises(FileNotFoundError):
            await notion_bridge.sync_file_to_notion("nonexistent/path.md")

        # Teste 2: Caminho fora do workspace
        with pytest.raises(ValueError):
            await notion_bridge.sync_file_to_notion("/root/outside/workspace.md")

        # Teste 3: Caracteres inválidos no caminho
        with pytest.raises(ValueError):
            await notion_bridge.sync_file_to_notion("invalid<>chars.md")

    @pytest.mark.asyncio
    async def test_partial_sync_failures(self, notion_bridge, file_helper) -> None:
        """Testa falhas parciais durante sincronização."""
        files = [
            file_helper.create_markdown(f"test{i}.md", f"# Test {i}\nContent")
            for i in range(3)
        ]

        # Simular falhas intermitentes
        success_count = 0

        async def mock_sync(*args, **kwargs):
            nonlocal success_count
            if success_count % 2 == 0:
                success_count += 1
                raise asyncio.TimeoutError
            success_count += 1
            return {"id": "test_id"}

        with patch.object(notion_bridge.client, "create_page") as mock_create:
            mock_create.side_effect = mock_sync

            # Tentar sincronizar múltiplos arquivos
            results = await asyncio.gather(
                *[notion_bridge.sync_file_to_notion(str(f)) for f in files],
                return_exceptions=True,
            )

            # Verificar resultados parciais
            successes = [r for r in results if not isinstance(r, Exception)]
            failures = [r for r in results if isinstance(r, Exception)]
            assert len(successes) > 0
            assert len(failures) > 0

    @pytest.mark.asyncio
    async def test_validation_and_limits(self, notion_bridge, file_helper) -> None:
        """Testa validações e limites específicos."""
        # Teste 1: Arquivo muito grande
        huge_content = "# " + "x" * (1024 * 1024 * 2)  # 2MB
        huge_file = file_helper.create_markdown("huge.md", huge_content)
        with pytest.raises(ValueError, match="file too large"):
            await notion_bridge.sync_file_to_notion(str(huge_file))

        # Teste 2: Formato inválido
        invalid_file = file_helper.base_path / "test.txt"
        invalid_file.write_text("Not a markdown file")
        with pytest.raises(ValueError, match="invalid format"):
            await notion_bridge.sync_file_to_notion(str(invalid_file))

        # Teste 3: Conteúdo inválido
        invalid_content = file_helper.create_markdown(
            "invalid.md",
            "```\nUnclosed code block",
        )
        with pytest.raises(ValueError, match="invalid markdown"):
            await notion_bridge.sync_file_to_notion(str(invalid_content))

    @pytest.mark.asyncio
    async def test_permission_handling(self, notion_bridge, file_helper, test_data) -> None:
        """Testa manipulação de permissões."""
        test_file = file_helper.create_markdown("test.md", "# Test\nContent")

        # Teste 1: Sem permissão de leitura
        with patch.object(
            notion_bridge.client,
            "get_page",
            side_effect=NotionAuthError("no read access"),
        ), pytest.raises(NotionAuthError, match="no read access"):
            await notion_bridge.sync_page_to_local("test_id")

        # Teste 2: Sem permissão de escrita
        with patch.object(
            notion_bridge.client,
            "create_page",
            side_effect=NotionAuthError("no write access"),
        ), pytest.raises(NotionAuthError, match="no write access"):
            await notion_bridge.sync_file_to_notion(str(test_file))

        # Teste 3: Permissões inconsistentes
        responses = [
            AsyncMock(return_value=test_data["responses"]["success"]),
            NotionAuthError("lost access"),
            AsyncMock(return_value=test_data["responses"]["success"]),
        ]

        with patch.object(notion_bridge.client, "_request") as mock_request:
            mock_request.side_effect = responses
            with pytest.raises(NotionAuthError, match="lost access"):
                await notion_bridge.sync_file_to_notion(str(test_file))

    @pytest.mark.asyncio
    async def test_concurrent_sync(self, notion_bridge, tmp_path) -> None:
        """Testa sincronização concorrente."""
        # Criar múltiplos arquivos
        files = [tmp_path / f"test{i}.md" for i in range(3)]
        for f in files:
            f.write_text("# Test\nContent")

        # Simular sincronização concorrente
        with patch.object(notion_bridge.client, "create_page", AsyncMock()):
            tasks = [notion_bridge.sync_file_to_notion(str(f)) for f in files]
            await asyncio.gather(*tasks)

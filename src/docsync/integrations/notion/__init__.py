"""DOCSYNC Notion Integration.
=========================

Módulo de integração entre DOCSYNC e Notion, permitindo sincronização
bidirecional de documentos e gerenciamento de conteúdo.

Classes Principais
----------------
- NotionSyncMonitor: Monitor de sincronização bidirecional
- NotionBridge: Interface de comunicação com a API do Notion
- NotionConfig: Configuração da integração
- NotionMapping: Mapeamento entre diretórios locais e páginas Notion
- NotionClient: Cliente HTTP para API do Notion

Uso Básico
---------
```python
from docsync.integrations.notion import NotionConfig, NotionMapping, NotionSyncMonitor
from pathlib import Path

# Configurar integração
config = NotionConfig(
    token='seu_token_aqui',
    workspace_id='seu_workspace',
    mappings=[
        NotionMapping(
            source_path=Path('./docs'),
            target_id='id_pagina_notion'
        )
    ]
)

# Criar e iniciar monitor
monitor = NotionSyncMonitor(config)
await monitor.start()
```

Recursos
--------
- Sincronização bidirecional automática
- Interface de monitoramento em tempo real
- Tratamento robusto de erros
- Suporte a múltiplos mapeamentos
- Logging detalhado de operações
"""

import logging

from .bridge import NotionBridge
from .client import NotionClient
from .config import NotionConfig
from .sync_monitor import NotionSyncMonitor, SyncFileHandler, SyncStats
from .types import NotionDatabase, NotionPage

__version__ = "0.1.0"
__author__ = "DOCSYNC Team"

# Configuração padrão de logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Constantes do módulo
DEFAULT_POLL_INTERVAL = 30  # segundos
DEFAULT_ERROR_RETRY_INTERVAL = 60  # segundos
DEFAULT_REFRESH_RATE = 4  # atualizações por segundo

# Tipos de evento suportados
SUPPORTED_EVENTS = {"created", "modified", "deleted"}

# Estados de sincronização
SYNC_STATES = {
    "initializing": "Iniciando...",
    "running": "Em execução",
    "error": "Erro",
    "stopped": "Parado",
}

# Configurações de timeout
TIMEOUTS = {"connect": 10, "read": 30, "write": 30}  # segundos

__all__ = [
    "NotionBridge",
    "NotionClient",
    "NotionConfig",
    "NotionDatabase",
    "NotionMapping",
    "NotionPage",
    "NotionSyncMonitor",
    "SyncFileHandler",
    "SyncStats",
]

"""Interface base para agentes de sincronização."""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class SyncAgentState(Enum):
    """Estados possíveis de um agente de sincronização."""

    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    CONFLICT = "conflict"
    WAITING = "waiting"
    COMPLETED = "completed"


class SyncAgentCapability(Enum):
    """Capacidades suportadas pelos agentes."""

    SYNC = "sync"
    CONFLICT_RESOLUTION = "conflict_resolution"
    VERSION_CONTROL = "version_control"
    COLLABORATIVE = "collaborative"
    AI_ENHANCED = "ai_enhanced"


class SyncAgent(ABC):
    """Interface base para agentes de sincronização."""

    def __init__(
        self,
        agent_id: str,
        workspace_path: Path,
        capabilities: Optional[Dict[SyncAgentCapability, bool]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Inicializa um agente de sincronização.

        Args:
            agent_id: Identificador único do agente
            workspace_path: Diretório de trabalho do agente
            capabilities: Dicionário de capacidades suportadas
            config: Configurações adicionais
        """
        self.agent_id = agent_id
        self.workspace_path = Path(workspace_path)
        self.capabilities = capabilities or {cap: False for cap in SyncAgentCapability}
        self.config = config or {}
        self.state = SyncAgentState.IDLE
        self.logger = logging.getLogger(f"docsync.agent.{agent_id}")

        # Criar diretório de trabalho
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def sync(self, doc_path: Path) -> Dict[str, Any]:
        """Sincroniza um documento.

        Args:
            doc_path: Caminho do documento

        Returns:
            Dict com resultado da sincronização
        """
        pass

    @abstractmethod
    async def resolve_conflict(
        self, doc_path: Path, conflicts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflitos de sincronização.

        Args:
            doc_path: Caminho do documento
            conflicts: Detalhes dos conflitos

        Returns:
            Dict com resultado da resolução
        """
        pass

    @abstractmethod
    async def check_version(self, doc_path: Path) -> Dict[str, Any]:
        """Verifica versão de um documento.

        Args:
            doc_path: Caminho do documento

        Returns:
            Dict com informações de versão
        """
        pass

    async def get_state(self) -> Dict[str, Any]:
        """Retorna estado atual do agente."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "capabilities": {k.value: v for k, v in self.capabilities.items()},
            "workspace": str(self.workspace_path),
        }

    async def set_state(self, state: SyncAgentState):
        """Atualiza estado do agente."""
        self.state = state
        self.logger.info("Agent %s state changed to %s", self.agent_id, state.value)

"""Gerenciamento de estados de sincronização."""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SyncState(Enum):
    """Estados possíveis de sincronização."""

    UNSYNCED = "unsynced"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncVersion:
    """Versão de um documento sincronizado."""

    def __init__(
        self,
        doc_path: Path,
        version: int,
        timestamp: datetime,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.doc_path = doc_path
        self.version = version
        self.timestamp = timestamp
        self.agent_id = agent_id
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "doc_path": str(self.doc_path),
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncVersion":
        """Cria instância a partir de dicionário."""
        return cls(
            doc_path=Path(data["doc_path"]),
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_id=data["agent_id"],
            metadata=data.get("metadata"),
        )


class SyncStateManager:
    """Gerencia estados de sincronização."""

    def __init__(self, state_dir: Path):
        """Inicializa gerenciador de estados.

        Args:
            state_dir: Diretório para armazenar estados
        """
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "sync_state.json"
        self.logger = logging.getLogger("docsync.state")

        # Criar diretório de estados
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Carregar estados salvos
        self.states: Dict[str, Dict[str, Any]] = {}
        if self.state_file.exists():
            self.states = self._load_states()

    def _load_states(self) -> Dict[str, Dict[str, Any]]:
        """Carrega estados salvos."""
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("Failed to load states: %s", e)
            return {}

    def _save_states(self):
        """Salva estados."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.states, f, indent=2)
        except Exception as e:
            self.logger.error("Failed to save states: %s", e)

    def get_doc_state(
        self, doc_path: Path, agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtém estado de um documento.

        Args:
            doc_path: Caminho do documento
            agent_id: ID opcional do agente

        Returns:
            Dict com estado do documento
        """
        doc_key = str(doc_path)
        state = self.states.get(doc_key, {})

        if agent_id:
            return state.get(
                agent_id,
                {"state": SyncState.UNSYNCED.value, "version": None, "timestamp": None},
            )
        return state

    def update_doc_state(
        self,
        doc_path: Path,
        agent_id: str,
        state: SyncState,
        version: Optional[SyncVersion] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Atualiza estado de um documento.

        Args:
            doc_path: Caminho do documento
            agent_id: ID do agente
            state: Novo estado
            version: Versão opcional
            metadata: Metadados opcionais
        """
        doc_key = str(doc_path)
        if doc_key not in self.states:
            self.states[doc_key] = {}

        self.states[doc_key][agent_id] = {
            "state": state.value,
            "version": version.to_dict() if version else None,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self._save_states()
        self.logger.info(
            "Updated state for doc %s agent %s: %s", doc_path, agent_id, state.value
        )

    def get_doc_versions(self, doc_path: Path) -> List[SyncVersion]:
        """Obtém histórico de versões de um documento.

        Args:
            doc_path: Caminho do documento

        Returns:
            Lista de versões ordenada por timestamp
        """
        doc_key = str(doc_path)
        state = self.states.get(doc_key, {})

        versions = []
        for agent_id, agent_state in state.items():
            if agent_state.get("version"):
                version = SyncVersion.from_dict(agent_state["version"])
                versions.append(version)

        return sorted(versions, key=lambda v: v.timestamp)

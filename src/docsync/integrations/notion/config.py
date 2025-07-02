"""DOCSYNC Notion Config.
====================

Define as classes de configuração para integração com o Notion.

Classes
-------
NotionConfig: Configuração principal da integração
NotionMapping: Mapeamento entre diretório local e página/database Notion
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NotionMapping:
    """Mapeamento entre diretório local e página/database Notion."""

    source_path: Path
    target_id: str
    sync_mode: str = "bidirectional"  # bidirectional, upload_only, download_only
    file_patterns: list[str] = None  # Ex: ["*.md", "*.txt"]
    ignore_patterns: list[str] = None  # Ex: ["*.tmp", ".*"]
    metadata: dict[str, Any] = None

    def __post_init__(self):
        # Garantir que source_path seja Path
        if isinstance(self.source_path, str):
            self.source_path = Path(self.source_path)

        # Valores padrão para patterns
        if self.file_patterns is None:
            self.file_patterns = ["*.md", "*.txt", "*.rst"]
        if self.ignore_patterns is None:
            self.ignore_patterns = [".*", "*.tmp", "*.bak", "__pycache__"]
        if self.metadata is None:
            self.metadata = {}

    def validate(self) -> bool:
        """Valida o mapeamento."""
        if not self.source_path.exists():
            msg = f"Diretório fonte não existe: {self.source_path}"
            raise ValueError(msg)
        if not self.source_path.is_dir():
            msg = f"Source path deve ser um diretório: {self.source_path}"
            raise ValueError(msg)
        if not self.target_id:
            msg = "Target ID é obrigatório"
            raise ValueError(msg)
        return True


@dataclass
class NotionConfig:
    """Configuração principal da integração Notion."""

    token: str
    workspace_id: str
    mappings: list[NotionMapping]
    base_url: str = "https://api.notion.com/v1"
    version: str = "2022-06-28"
    auto_retry: bool = True
    max_retries: int = 3
    retry_delay: int = 5
    timeout: dict[str, int] = None
    headers: dict[str, str] = None

    def __post_init__(self):
        # Configurar headers padrão
        if self.headers is None:
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.version,
                "Content-Type": "application/json",
            }

        # Configurar timeouts padrão
        if self.timeout is None:
            self.timeout = {"connect": 10, "read": 30, "write": 30}

    def validate(self) -> bool:
        """Valida a configuração."""
        if not self.token:
            msg = "Token é obrigatório"
            raise ValueError(msg)
        if not self.workspace_id:
            msg = "Workspace ID é obrigatório"
            raise ValueError(msg)
        if not self.mappings:
            msg = "Pelo menos um mapeamento é necessário"
            raise ValueError(msg)

        # Validar cada mapeamento
        for mapping in self.mappings:
            mapping.validate()

        return True

    def get_headers(self) -> dict[str, str]:
        """Retorna os headers para requisições."""
        return self.headers.copy()

    def get_timeout(self) -> dict[str, int]:
        """Retorna as configurações de timeout."""
        return self.timeout.copy()


# Modos de sincronização suportados
SYNC_MODES = {
    "bidirectional": "Sincronização em ambas as direções",
    "upload_only": "Apenas upload local → Notion",
    "download_only": "Apenas download Notion → local",
}

# Configurações padrão
DEFAULT_CONFIG = {
    "version": "2022-06-28",
    "base_url": "https://api.notion.com/v1",
    "auto_retry": True,
    "max_retries": 3,
    "retry_delay": 5,
    "file_patterns": ["*.md", "*.txt", "*.rst"],
    "ignore_patterns": [".*", "*.tmp", "*.bak", "__pycache__"],
}

# Configurações finalizadas acima

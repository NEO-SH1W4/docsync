"""Classes base para plugins do DocSync."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PluginMetadata:
    """Metadados de plugin."""

    name: str
    version: str
    description: str
    author: str
    extensions: list[str]


class DocumentFormat:
    """Classe base para plugins de formato."""

    def __init__(self) -> None:
        """Inicializa plugin."""
        self.metadata = self.get_metadata()
        self.config = {}

    def get_metadata(self) -> PluginMetadata:
        """Retorna metadados do plugin.

        Returns:
            PluginMetadata: Metadados

        Raises:
            NotImplementedError: Se não implementado
        """
        raise NotImplementedError

    def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa plugin com configuração.

        Args:
            config: Configuração do plugin
        """
        self.config = config

    def cleanup(self) -> None:
        """Limpa recursos do plugin."""

    def can_handle(self, file_path: Path) -> bool:
        """Verifica se plugin pode processar arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            bool: Se pode processar
        """
        return file_path.suffix.lower() in self.metadata.extensions

    def read_document(self, file_path: Path) -> dict[str, Any]:
        """Lê e processa documento.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dict[str, Any]: Conteúdo processado

        Raises:
            NotImplementedError: Se não implementado
        """
        raise NotImplementedError

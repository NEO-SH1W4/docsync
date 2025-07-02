"""Implementação principal do DocSync."""

import logging
from pathlib import Path
from typing import Optional, Union

from rich.console import Console
from rich.logging import RichHandler

from docsync.utils.config import load_config


class DocSync:
    """Sistema de sincronização de documentação."""

    def __init__(
        self,
        base_path: Union[str, Path],
        config_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Inicializa o DocSync.

        Args:
            base_path: Diretório base da documentação
            config_path: Caminho opcional para arquivo de configuração
        """
        self.base_path = Path(base_path)
        self.config_path = Path(config_path) if config_path else None
        self.console = Console()

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(console=self.console)],
        )
        self.logger = logging.getLogger("docsync")

        # Carregar configuração
        self.config = load_config(self.config_path) if self.config_path else {}

        # Criar diretório base se não existir
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("✨ DocSync inicializado em %s", self.base_path)

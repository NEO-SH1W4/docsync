"""
DocSync Core - Sistema de sincronização e gerenciamento de documentação.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union


from .config import load_config
from .plugins.base import DocumentFormat
from .utils.logger import setup_logger
from .utils.manager import SyncManager
from .utils.validation import validate_path


class DocSync:
    """Sistema de gerenciamento de documentação com suporte GUARDRIVE."""

    def __init__(
        self,
        base_path: Union[str, Path],
        config_path: Optional[Union[str, Path]] = None,
        templates_path: Optional[Union[str, Path]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Inicializa o sistema DocSync.

        Args:
            base_path: Diretório base de trabalho
            config_path: Caminho para arquivo de configuração
            templates_path: Diretório de templates
            logger: Logger customizado opcional
        """
        self.base_path = Path(base_path)
        self.config_path = (
            Path(config_path) if config_path else self.base_path / "docsync.yml"
        )
        self.templates_path = (
            Path(templates_path) if templates_path else self.base_path / "templates"
        )

        # Configurar logging
        self.logger = logger or setup_logger("docsync")

        # Validar e criar diretórios
        for path in [self.base_path, self.templates_path]:
            validate_path(path, create=True)

        # Carregar configuração
        self.config = load_config(self.config_path)

        # Inicializar gerenciador de sync
        self.sync_manager = SyncManager(self.base_path, self.config)

        # Registro de plugins
        self._plugins: Dict[str, DocumentFormat] = {}

        self.logger.info("✨ DocSync inicializado com sucesso")

    def register_plugin(self, plugin: DocumentFormat) -> None:
        """
        Registra um plugin de formato de documento.

        Args:
            plugin: Instância do plugin
        """
        try:
            # Inicializar plugin
            plugin.initialize(
                self.config.get("plugins", {}).get(plugin.metadata.name, {})
            )

            # Registrar plugin
            self._plugins[plugin.metadata.name] = plugin
            self.logger.info(
                f"✨ Plugin registrado: {plugin.metadata.name} v{plugin.metadata.version}"
            )

        except Exception as e:
            self.logger.error(
                f"❌ Erro ao registrar plugin {plugin.metadata.name}: {e}"
            )
            raise

    def unregister_plugin(self, name: str) -> None:
        """
        Remove registro de um plugin.

        Args:
            name: Nome do plugin
        """
        if name in self._plugins:
            try:
                self._plugins[name].cleanup()
                del self._plugins[name]
                self.logger.info(f"🗑️ Plugin removido: {name}")
            except Exception as e:
                self.logger.error(f"❌ Erro ao remover plugin {name}: {e}")
                raise

    def get_plugin(self, name: str) -> Optional[DocumentFormat]:
        """
        Obtém plugin pelo nome.

        Args:
            name: Nome do plugin

        Returns:
            Optional[DocumentFormat]: Plugin ou None se não encontrado
        """
        return self._plugins.get(name)

    def find_plugin_for_file(self, file_path: Path) -> Optional[DocumentFormat]:
        """
        Encontra plugin capaz de processar arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Optional[DocumentFormat]: Plugin ou None se não encontrado
        """
        for plugin in self._plugins.values():
            if plugin.can_handle(file_path):
                return plugin
        return None

    def process_document(
        self, file_path: Path, plugin_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Processa documento usando plugin apropriado.

        Args:
            file_path: Caminho do arquivo
            plugin_name: Nome do plugin (opcional)
            **kwargs: Argumentos adicionais para plugin

        Returns:
            Dict[str, Any]: Resultado do processamento

        Raises:
            ValueError: Se nenhum plugin puder processar arquivo
        """
        # Encontrar plugin
        plugin = None
        if plugin_name:
            plugin = self.get_plugin(plugin_name)
            if not plugin:
                raise ValueError(f"Plugin não encontrado: {plugin_name}")
        else:
            plugin = self.find_plugin_for_file(file_path)
            if not plugin:
                raise ValueError(f"Nenhum plugin pode processar: {file_path}")

        try:
            # Processar documento
            self.logger.info(f"🔄 Processando {file_path} com {plugin.metadata.name}")
            result = plugin.read_document(file_path)

            # Adicionar metadados
            result["plugin"] = plugin.metadata.name
            result["file_path"] = str(file_path)

            return result

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar {file_path}: {e}")
            raise

    def sync_directories(
        self, source: Union[str, Path], target: Union[str, Path], **kwargs
    ) -> Dict[str, int]:
        """
        Sincroniza diretórios.

        Args:
            source: Diretório fonte
            target: Diretório destino
            **kwargs: Argumentos para SyncManager

        Returns:
            Dict[str, int]: Estatísticas de sincronização
        """
        self.logger.info(
            f"🔄 Sincronizando diretórios:\nFonte: {source}\nDestino: {target}"
        )
        return self.sync_manager.sync(source, target, **kwargs)

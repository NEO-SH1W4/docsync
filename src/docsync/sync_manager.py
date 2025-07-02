"""Módulo de gerenciamento de sincronização do DocSync.

Implementa a lógica de sincronização bidirecional entre GUARDRIVE_DOCS e AREA_DEV,
incluindo monitoramento de arquivos, controle de versão e validação de segurança.

Author: DocSync Team
Date: 2025-06-03
"""

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import aiofiles
import aiogit
from croniter import croniter
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import Config, DocumentType, PathMappingConfig
from .utils import setup_logger

# Configuração do logging
logger = setup_logger(__name__)


class SyncStatus(Enum):
    """Status possíveis de sincronização."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class FileMetadata:
    """Metadados de arquivo para controle de sincronização."""

    path: Path
    hash: str
    modified_time: float
    size: int
    doc_type: DocumentType
    last_sync: datetime
    status: SyncStatus


class DocumentHandler:
    """Manipulador de documentos específico por tipo."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.supported_extensions = config.get("file_extensions", [])
        self.preserve_metadata = config.get("preserve_metadata", True)
        self.convert_formats = config.get("convert_formats", False)
        self.validate_links = config.get("validate_links", True)
        self.check_references = config.get("check_references", True)

    async def process_file(self, file_path: Path, target_path: Path) -> bool:
        """Processa um arquivo conforme suas configurações específicas."""
        try:
            if not self._is_supported_file(file_path):
                logger.warning(f"Tipo de arquivo não suportado: {file_path}")
                return False

            # Validação de links e referências
            if self.validate_links:
                await self._validate_links(file_path)
            if self.check_references:
                await self._check_references(file_path)

            # Conversão de formato se necessário
            if self.convert_formats:
                target_path = await self._convert_format(file_path, target_path)

            # Preservação de metadados
            metadata = await self._extract_metadata(file_path)

            # Copia o arquivo
            await self._copy_file(file_path, target_path)

            # Restaura metadados se necessário
            if self.preserve_metadata:
                await self._restore_metadata(target_path, metadata)

            return True

        except Exception as e:
            logger.exception(f"Erro ao processar arquivo {file_path}: {e}")
            return False

    def _is_supported_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower()[1:] in self.supported_extensions

    async def _validate_links(self, file_path: Path) -> None:
        # Implementar validação de links no documento
        pass

    async def _check_references(self, file_path: Path) -> None:
        # Implementar verificação de referências
        pass

    async def _convert_format(self, source: Path, target: Path) -> Path:
        # Implementar conversão de formato se necessário
        return target

    async def _extract_metadata(self, file_path: Path) -> dict:
        # Extrair metadados do arquivo
        return {}

    async def _restore_metadata(self, file_path: Path, metadata: dict) -> None:
        # Restaurar metadados no arquivo
        pass

    async def _copy_file(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        await aiofiles.os.copy(source, target)


class VersionController:
    """Controlador de versão para documentos."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.enabled = config.get("enabled", True)
        self.provider = config.get("provider", "git")
        self.backup_enabled = config.get("backup_enabled", True)
        self.backup_interval = config.get("backup_interval", 3600)
        self.retention_days = config.get("retention_days", 30)
        self.commit_template = config.get(
            "commit_message_template",
            "doc: {action} - {path}",
        )

    async def initialize_repo(self, path: Path) -> None:
        """Inicializa repositório de controle de versão."""
        if not self.enabled:
            return

        try:
            repo = await aiogit.Repository.create(path)
            await repo.init()
            logger.info(f"Repositório inicializado em {path}")
        except Exception as e:
            logger.exception(f"Erro ao inicializar repositório: {e}")

    async def commit_changes(self, path: Path, action: str) -> bool:
        """Registra alterações no controle de versão."""
        if not self.enabled:
            return True

        try:
            repo = await aiogit.Repository.open(path)
            await repo.add_all()
            message = self.commit_template.format(action=action, path=path)
            await repo.commit(message)
            return True
        except Exception as e:
            logger.exception(f"Erro ao commitar alterações: {e}")
            return False

    async def create_backup(self, path: Path) -> bool:
        """Cria backup do documento."""
        if not self.backup_enabled:
            return True

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = path.parent / "backups" / f"{path.name}_{timestamp}"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            await aiofiles.os.copy(path, backup_path)
            return True
        except Exception as e:
            logger.exception(f"Erro ao criar backup: {e}")
            return False


class FileSystemMonitor(FileSystemEventHandler):
    """Monitor de alterações no sistema de arquivos."""

    def __init__(self, sync_manager: "SyncManager") -> None:
        self.sync_manager = sync_manager
        self.observer = Observer()

    def start(self) -> None:
        """Inicia monitoramento de diretórios."""
        for path in self.sync_manager.watch_paths:
            self.observer.schedule(self, path, recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """Para monitoramento de diretórios."""
        self.observer.stop()
        self.observer.join()

    def on_modified(self, event) -> None:
        """Manipula eventos de modificação de arquivo."""
        if event.is_directory:
            return
        asyncio.create_task(self.sync_manager.handle_file_change(Path(event.src_path)))


class SyncManager:
    """Gerenciador principal de sincronização."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.guardrive_config = config.guardrive
        self.sync_config = config.sync

        # Inicializa handlers de documentos
        self.doc_handlers = {
            doc_type: DocumentHandler(handler_config)
            for doc_type, handler_config in self.guardrive_config.doc_handlers.items()
        }

        # Inicializa controle de versão
        self.version_control = VersionController(self.guardrive_config.version_control)

        # Caminhos para monitoramento
        self.watch_paths = self._setup_watch_paths()

        # Monitor de sistema de arquivos
        self.monitor = FileSystemMonitor(self)

        # Cache de metadados
        self.file_metadata: dict[Path, FileMetadata] = {}

        # Scheduler para sincronização programada
        self.scheduler = asyncio.create_task(self._run_scheduler())

    def _setup_watch_paths(self) -> set[Path]:
        """Configura caminhos para monitoramento."""
        paths = set()
        base_path = Path(self.guardrive_config.base_path)

        # Adiciona caminhos da documentação oficial
        docs_path = base_path / self.guardrive_config.docs_path
        paths.add(docs_path)

        # Adiciona caminhos da área de desenvolvimento
        dev_path = base_path / self.guardrive_config.dev_path
        paths.add(dev_path)

        return paths

    async def start(self) -> None:
        """Inicia o gerenciador de sincronização."""
        logger.info("Iniciando gerenciador de sincronização...")

        # Inicializa repositórios de versão
        for path in self.watch_paths:
            await self.version_control.initialize_repo(path)

        # Inicia monitoramento de arquivos
        if self.sync_config.real_time_sync:
            self.monitor.start()

        # Realiza sincronização inicial
        await self.sync_all()

        logger.info("Gerenciador de sincronização iniciado com sucesso")

    async def stop(self) -> None:
        """Para o gerenciador de sincronização."""
        logger.info("Parando gerenciador de sincronização...")

        if self.sync_config.real_time_sync:
            self.monitor.stop()

        self.scheduler.cancel()

        logger.info("Gerenciador de sincronização parado com sucesso")

    async def sync_all(self) -> None:
        """Realiza sincronização completa dos diretórios."""
        logger.info("Iniciando sincronização completa...")

        try:
            for mapping in self.guardrive_config.path_mappings:
                await self._sync_directory_pair(
                    Path(mapping.source_path),
                    Path(mapping.target_path),
                    mapping.doc_type,
                )

            logger.info("Sincronização completa finalizada com sucesso")

        except Exception as e:
            logger.exception(f"Erro durante sincronização completa: {e}")

    async def handle_file_change(self, file_path: Path) -> None:
        """Manipula alteração em arquivo."""
        try:
            # Verifica se arquivo deve ser ignorado
            if self._should_ignore(file_path):
                return

            # Identifica mapeamento correspondente
            mapping = self._find_mapping_for_file(file_path)
            if not mapping:
                logger.warning(f"Nenhum mapeamento encontrado para {file_path}")
                return

            # Determina caminho de destino
            target_path = self._get_target_path(file_path, mapping)

            # Processa arquivo
            handler = self.doc_handlers.get(
                mapping.doc_type.value,
                self.doc_handlers["default"],
            )

            # Cria backup se necessário
            if self.guardrive_config.version_control.backup_enabled:
                await self.version_control.create_backup(file_path)

            # Processa e sincroniza arquivo
            success = await handler.process_file(file_path, target_path)

            if success:
                # Atualiza metadados
                await self._update_metadata(file_path)
                await self._update_metadata(target_path)

                # Registra no controle de versão
                await self.version_control.commit_changes(file_path.parent, "update")

                logger.info(f"Arquivo {file_path} sincronizado com sucesso")

        except Exception as e:
            logger.exception(f"Erro ao processar alteração em {file_path}: {e}")

    def _should_ignore(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser ignorado."""
        name = file_path.name
        return any(pattern in name for pattern in self.sync_config.ignore_patterns)

    def _find_mapping_for_file(self, file_path: Path) -> Optional[PathMappingConfig]:
        """Encontra mapeamento correspondente para um arquivo."""
        str_path = str(file_path)
        for mapping in self.guardrive_config.path_mappings:
            if str_path.startswith((mapping.source_path, mapping.target_path)):
                return mapping
        return None

    def _get_target_path(self, source_path: Path, mapping: PathMappingConfig) -> Path:
        """Determina caminho de destino para um arquivo."""
        if str(source_path).startswith(mapping.source_path):
            relative_path = source_path.relative_to(mapping.source_path)
            return Path(mapping.target_path) / relative_path
        relative_path = source_path.relative_to(mapping.target_path)
        return Path(mapping.source_path) / relative_path

    async def _update_metadata(self, file_path: Path) -> None:
        """Atualiza metadados de arquivo."""
        try:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
                file_hash = hashlib.sha256(content).hexdigest()

            stat = await aiofiles.os.stat(file_path)

            self.file_metadata[file_path] = FileMetadata(
                path=file_path,
                hash=file_hash,
                modified_time=stat.st_mtime,
                size=stat.st_size,
                doc_type=self._get_doc_type(file_path),
                last_sync=datetime.now(),
                status=SyncStatus.COMPLETED,
            )

        except Exception as e:
            logger.exception(f"Erro ao atualizar metadados de {file_path}: {e}")

    def _get_doc_type(self, file_path: Path) -> DocumentType:
        """Determina tipo de documento baseado no caminho."""
        str_path = str(file_path)
        for mapping in self.guardrive_config.path_mappings:
            if str_path.startswith((mapping.source_path, mapping.target_path)):
                return mapping.doc_type
        return DocumentType.TECHNICAL

    async def _run_scheduler(self) -> None:
        """Executa scheduler de sincronização programada."""
        try:
            while True:
                # Verifica próxima execução
                cron = croniter(self.guardrive_config.sync_schedule)
                next_run = cron.get_next(datetime)
                now = datetime.now()

                # Aguarda até próxima execução
                delay = (next_run - now).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)

                # Executa sincronização
                await self.sync_all()

        except asyncio.CancelledError:
            logger.info("Scheduler de sincronização cancelado")
        except Exception as e:
            logger.exception(f"Erro no scheduler de sincronização: {e}")

    async def _sync_directory_pair(
        self,
        source: Path,
        target: Path,
        doc_type: DocumentType,
    ) -> None:
        """Sincroniza par de diretórios."""
        try:
            # Cria diretório de destino se necessário
            target.mkdir(parents=True, exist_ok=True)

            # Lista arquivos fonte
            async for entry in aiofiles.os.scandir(source):
                if entry.is_file():
                    source_file = Path(entry.path)
                    if self._should_ignore(source_file):
                        continue

                    # Determina caminho de destino
                    relative_path = source_file.relative_to(source)
                    target_file = target / relative_path

                    # Processa arquivo
                    handler = self.doc_handlers.get(
                        doc_type.value,
                        self.doc_handlers["default"],
                    )
                    await handler.process_file(source_file, target_file)

                elif entry.is_dir():
                    # Recursivamente sincroniza subdiretórios
                    source_dir = Path(entry.path)
                    target_dir = target / source_dir.name
                    await self._sync_directory_pair(source_dir, target_dir, doc_type)

        except Exception as e:
            logger.exception(
                f"Erro ao sincronizar diretórios {source} -> {target}: {e}"
            )

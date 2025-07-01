#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

import aiohttp
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from docsync.integrations.notion import (
    NotionBridge,
    NotionClient,
    NotionConfig,
    NotionMapping,
)


class SyncStats:
    """Estatísticas de sincronização"""

    def __init__(self):
        self.start_time = datetime.now()
        self.files_synced = 0
        self.bytes_transferred = 0
        self.last_sync = None
        self.errors = 0
        self.changes_local = 0
        self.changes_notion = 0
        self.status = "Iniciando..."
        self.current_operation = None
        self.sync_queue = set()
        self.notion_queue = set()


class SyncFileHandler(FileSystemEventHandler):
    """Handler para eventos do sistema de arquivos"""

    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__()

    def on_modified(self, event):
        """Trata modificações em arquivos"""
        if event.is_directory:
            return

        self.monitor.stats.changes_local += 1
        self.monitor.stats.sync_queue.add(event.src_path)
        self.monitor.stats.status = "Alteração local detectada"
        logging.info(f"Arquivo modificado: {event.src_path}")

    def on_created(self, event):
        """Trata criação de arquivos"""
        if event.is_directory:
            return

        self.monitor.stats.changes_local += 1
        self.monitor.stats.sync_queue.add(event.src_path)
        self.monitor.stats.status = "Novo arquivo local detectado"
        logging.info(f"Arquivo criado: {event.src_path}")

    def on_deleted(self, event):
        """Trata deleção de arquivos"""
        if event.is_directory:
            return

        self.monitor.stats.changes_local += 1
        self.monitor.stats.sync_queue.add(event.src_path)
        self.monitor.stats.status = "Deleção local detectada"
        logging.info(f"Arquivo deletado: {event.src_path}")


class NotionSyncMonitor:
    """Monitor de sincronização Notion-DOCSYNC"""

    def __init__(self, config: NotionConfig):
        self.config = config
        self.stats = SyncStats()
        self.console = Console()
        self.bridge = NotionBridge(config)
        self.observer = Observer()
        self.file_handler = SyncFileHandler(self)
        self._running = False
        self._notion_poll_task = None

    async def start(self):
        """Inicia o monitoramento"""
        try:
            # Inicializar bridge
            await self.bridge.initialize()

            # Configurar observador de arquivos
            for mapping in self.config.mappings:
                self.observer.schedule(
                    self.file_handler, str(mapping.source_path), recursive=True
                )

            self.observer.start()
            self._running = True

            # Iniciar polling do Notion
            self._notion_poll_task = asyncio.create_task(self._poll_notion_changes())

            # Iniciar interface
            await self._run_interface()

        except Exception as e:
            logging.error(f"Erro ao iniciar monitoramento: {e}")
            raise

    async def stop(self):
        """Para o monitoramento"""
        self._running = False
        self.observer.stop()
        if self._notion_poll_task:
            self._notion_poll_task.cancel()

    async def _poll_notion_changes(self):
        """Monitora alterações no Notion"""
        while self._running:
            try:
                for mapping in self.config.mappings:
                    changes = await self.bridge.client.get_recent_changes(
                        mapping.target_id
                    )
                    if changes:
                        self.stats.changes_notion += len(changes)
                        self.stats.notion_queue.update(page["id"] for page in changes)
                        self.stats.status = "Alterações Notion detectadas"

                await asyncio.sleep(30)  # Poll a cada 30 segundos

            except Exception as e:
                logging.error(f"Erro ao verificar alterações no Notion: {e}")
                self.stats.errors += 1
                self.stats.status = "Erro ao verificar Notion"
                await asyncio.sleep(60)  # Espera mais tempo em caso de erro

    def _create_status_table(self) -> Table:
        """Cria tabela de status"""
        table = Table(title="Status de Sincronização")

        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")

        # Tempo em execução
        uptime = datetime.now() - self.stats.start_time
        uptime_str = (
            f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        )

        # Adicionar linhas com métricas
        table.add_row("Status", self.stats.status)
        table.add_row("Tempo em Execução", uptime_str)
        table.add_row("Arquivos Sincronizados", str(self.stats.files_synced))
        table.add_row(
            "Dados Transferidos", f"{self.stats.bytes_transferred/1024:.2f} KB"
        )
        table.add_row("Alterações Locais", str(self.stats.changes_local))
        table.add_row("Alterações Notion", str(self.stats.changes_notion))
        table.add_row("Fila Local", str(len(self.stats.sync_queue)))
        table.add_row("Fila Notion", str(len(self.stats.notion_queue)))
        table.add_row("Erros", str(self.stats.errors))

        if self.stats.last_sync:
            last_sync = self.stats.last_sync.strftime("%H:%M:%S")
            table.add_row("Última Sincronização", last_sync)

        if self.stats.current_operation:
            table.add_row("Operação Atual", self.stats.current_operation)

        return table

    def _update_display(self) -> Layout:
        """Atualiza o layout da interface"""
        layout = Layout()

        # Criar seção principal
        layout.split(
            Layout(
                Panel(
                    self._create_status_table(),
                    title="DOCSYNC Monitor",
                    border_style="blue",
                )
            )
        )

        return layout

    async def _run_interface(self):
        """Executa a interface do monitor"""
        try:
            with Live(
                self._update_display(), refresh_per_second=4, console=self.console
            ) as live:
                while self._running:
                    # Processar fila de sincronização local
                    if self.stats.sync_queue:
                        path = self.stats.sync_queue.pop()
                        self.stats.current_operation = f"Sincronizando: {path}"
                        try:
                            # Aqui virá a lógica de sincronização
                            await self.bridge.sync_file_to_notion(path)
                            self.stats.files_synced += 1
                            self.stats.last_sync = datetime.now()
                        except Exception as e:
                            self.stats.errors += 1
                            logging.error(f"Erro ao sincronizar {path}: {e}")

                    # Processar fila do Notion
                    if self.stats.notion_queue:
                        page_id = self.stats.notion_queue.pop()
                        self.stats.current_operation = f"Baixando: {page_id}"
                        try:
                            # Aqui virá a lógica de download
                            await self.bridge.sync_page_to_local(page_id)
                            self.stats.files_synced += 1
                            self.stats.last_sync = datetime.now()
                        except Exception as e:
                            self.stats.errors += 1
                            logging.error(f"Erro ao baixar página {page_id}: {e}")

                    # Atualizar display
                    live.update(self._update_display())

                    # Pequena pausa para não sobrecarregar
                    await asyncio.sleep(0.25)

                    # Atualizar status
                    if not self.stats.sync_queue and not self.stats.notion_queue:
                        self.stats.status = "Aguardando alterações..."
                        self.stats.current_operation = None

        except Exception as e:
            logging.error(f"Erro na interface: {e}")
            self.stats.errors += 1
            raise


async def main():
    """Função principal"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Configuração do monitor
    config = NotionConfig(
        token="seu_token_aqui",
        workspace_id="GENESIS_LAB",
        mappings=[
            NotionMapping(source_path=Path("./docs"), target_id="pagina_destino_id")
        ],
    )

    # Criar e iniciar monitor
    monitor = NotionSyncMonitor(config)

    try:
        await monitor.start()
    except KeyboardInterrupt:
        print("\nEncerrando monitoramento...")
        await monitor.stop()
    except Exception as e:
        print(f"Erro: {e}")
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())

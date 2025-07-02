#!/usr/bin/env python3
"""
Script principal para execução do sistema DocSync.

Inicializa e gerencia o processo de sincronização da documentação,
incluindo configuração, monitoramento e controle de execução.

Author: DocSync Team
Date: 2025-06-03
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from src.docsync.config import Config, load_config
from src.docsync.sync_manager import SyncManager
from src.docsync.utils import setup_logger

# Configuração do logging
logger = setup_logger(__name__)


class SyncController:
    """Controlador principal do sistema de sincronização."""

    def __init__(self):
        self.sync_manager: Optional[SyncManager] = None
        self.shutdown_event = asyncio.Event()
        self.config: Optional[Config] = None

    async def initialize(self, config_path: Path) -> bool:
        """
        Inicializa o sistema de sincronização.

        Args:
            config_path: Caminho para o arquivo de configuração

        Returns:
            bool: True se inicialização foi bem sucedida
        """
        try:
            # Carrega configuração
            config_dict = load_config(config_path)
            self.config = Config(**config_dict)

            # Configura logging global
            logging.getLogger().setLevel(self.config.log_level)

            # Inicializa gerenciador de sincronização
            self.sync_manager = SyncManager(self.config)

            # Configura handlers de sinais
            self._setup_signal_handlers()

            # Inicia sincronização
            await self.sync_manager.start()

            logger.info("Sistema de sincronização inicializado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao inicializar sistema: {e}")
            return False

    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler para sinais de término."""
        logger.info(f"Sinal {signum} recebido, iniciando desligamento...")
        self.shutdown_event.set()

    async def shutdown(self):
        """Realiza desligamento controlado do sistema."""
        try:
            if self.sync_manager:
                await self.sync_manager.stop()
            logger.info("Sistema encerrado com sucesso")
        except Exception as e:
            logger.error(f"Erro durante encerramento: {e}")

    @asynccontextmanager
    async def run_session(self, config_path: Path):
        """
        Gerencia uma sessão completa de sincronização.

        Args:
            config_path: Caminho para arquivo de configuração
        """
        try:
            if await self.initialize(config_path):
                yield self
            else:
                logger.error("Falha na inicialização do sistema")
                yield None
        finally:
            await self.shutdown()

    async def run(self):
        """Executa o loop principal de sincronização."""
        try:
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Execução cancelada")
        except Exception as e:
            logger.error(f"Erro durante execução: {e}")


def parse_args():
    """Processa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema de Sincronização de Documentação DocSync"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("docsync_sync.yaml"),
        help="Caminho para arquivo de configuração (default: docsync_sync.yaml)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Ativa logging detalhado"
    )
    return parser.parse_args()


async def main():
    """Função principal de execução."""
    args = parse_args()

    # Configura logging verbose se solicitado
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Verifica arquivo de configuração
    if not args.config.exists():
        logger.error(f"Arquivo de configuração não encontrado: {args.config}")
        return 1

    # Executa sistema
    async with SyncController().run_session(args.config) as controller:
        if controller:
            await controller.run()
        else:
            return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

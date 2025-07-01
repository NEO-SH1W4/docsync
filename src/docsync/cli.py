"""
Interface de linha de comando do DocSync.
"""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from . import __version__
from .core import DocSync

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """DocSync - Sistema de sincronização e gerenciamento de documentação."""
    pass


@cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="Arquivo de configuração YAML",
)
def sync(path: Path, config: Optional[Path] = None):
    """Sincroniza diretório de documentação."""
    try:
        doc_sync = DocSync(path, config_path=config)
        # TODO: Implementar sincronização
        console.print("✨ Sincronização concluída!")
    except Exception as e:
        console.print(f"❌ Erro: {e}", style="red")
        raise click.Abort()


def main():
    """Ponto de entrada principal."""
    try:
        cli()
    except Exception as e:
        console.print(f"❌ Erro fatal: {e}", style="red")
        raise click.Abort()

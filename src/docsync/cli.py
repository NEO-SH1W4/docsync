"""
DocSync command line interface.
"""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from . import __version__

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """DocSync - Documentation synchronization and management system."""


@cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="YAML configuration file",
)
def sync(path: Path, config: Optional[Path] = None):
    """Synchronize documentation directory."""
    try:
        # doc_sync = DocSync(path, config_path=config)  # TODO: Implement command
        # TODO: Implement synchronization
        console.print("✨ Synchronization completed!")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise click.Abort()


def main():
    """Main entry point."""
    try:
        cli()
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="red")
        raise click.Abort()

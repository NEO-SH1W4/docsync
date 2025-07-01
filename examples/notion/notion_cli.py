# notion_cli.py
import asyncio
import json
import logging
import os
from pathlib import Path

import click

from docsync.integrations.notion import NotionBridge, NotionConfig, NotionMapping

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@click.group()
def cli():
    """Ferramenta CLI para sincronização com Notion"""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Caminho para arquivo de configuração",
)
@click.option("--token", envvar="NOTION_TOKEN", help="Token de integração do Notion")
@click.option(
    "--workspace", envvar="NOTION_WORKSPACE", help="ID do workspace do Notion"
)
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True),
    help="Diretório fonte para sincronização",
)
@click.option("--target", "-t", help="ID do database/página alvo no Notion")
def sync(config, token, workspace, source, target):
    """Sincroniza documentos com o Notion"""

    async def do_sync():
        # Carregar configuração
        if config:
            with open(config) as f:
                config_data = json.load(f)
        else:
            config_data = {
                "token": token,
                "workspace_id": workspace,
                "mappings": [
                    {
                        "source_path": str(source),
                        "target_id": target,
                        "sync_type": "bidirectional",
                    }
                ],
            }

        notion_config = NotionConfig(
            token=config_data["token"],
            workspace_id=config_data["workspace_id"],
            mappings=[
                NotionMapping(
                    source_path=Path(m["source_path"]),
                    target_id=m["target_id"],
                    sync_type=m.get("sync_type", "bidirectional"),
                )
                for m in config_data["mappings"]
            ],
        )

        # Inicializar e executar sincronização
        bridge = NotionBridge(notion_config)
        await bridge.initialize()
        await bridge.sync()

    asyncio.run(do_sync())


@cli.command()
@click.option(
    "--token",
    envvar="NOTION_TOKEN",
    required=True,
    help="Token de integração do Notion",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="notion_config.json",
    help="Arquivo de saída",
)
def init(token, output):
    """Inicializa nova configuração do Notion"""

    async def do_init():
        # Criar configuração básica
        config = NotionConfig(
            token=token,
            workspace_id="",  # Será preenchido após verificação
            mappings=[],
        )

        # Verificar conexão
        bridge = NotionBridge(config)
        try:
            await bridge.initialize()
            click.echo("✓ Conexão com Notion estabelecida com sucesso!")

            # Salvar configuração
            config_data = {
                "token": token,
                "workspace_id": "",
                "mappings": [],
                "sync_interval": 300,
                "max_retries": 3,
                "retry_delay": 60,
            }

            with open(output, "w") as f:
                json.dump(config_data, f, indent=2)

            click.echo(f"✓ Configuração inicial salva em {output}")
            click.echo("i Edite o arquivo para adicionar seus mapeamentos")

        except Exception as e:
            click.echo(f"✗ Erro ao conectar com Notion: {e}", err=True)

    asyncio.run(do_init())


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Arquivo de configuração",
)
def validate(config):
    """Valida arquivo de configuração"""
    try:
        with open(config) as f:
            config_data = json.load(f)

        required = ["token", "workspace_id", "mappings"]
        for field in required:
            if field not in config_data:
                click.echo(f"✗ Campo obrigatório ausente: {field}", err=True)
                return

        for mapping in config_data["mappings"]:
            if "source_path" not in mapping or "target_id" not in mapping:
                click.echo(
                    "✗ Mapeamento inválido: necessário source_path e target_id",
                    err=True,
                )
                return

        click.echo("✓ Arquivo de configuração válido!")

    except Exception as e:
        click.echo(f"✗ Erro ao validar configuração: {e}", err=True)


if __name__ == "__main__":
    cli()

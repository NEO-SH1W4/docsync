# notion_sync_example.py
import asyncio
import logging
from pathlib import Path

from docsync.integrations.notion import NotionBridge, NotionConfig, NotionMapping

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    # Configurar integração com Notion
    config = NotionConfig(
        token="seu_token_aqui",  # Substitua pelo seu token
        workspace_id="seu_workspace_id",  # Substitua pelo seu workspace
        mappings=[
            NotionMapping(
                source_path=Path("./docs/technical"),
                target_id="id_database_documentacao_tecnica",  # ID do database no Notion
                sync_type="bidirectional",
            ),
            NotionMapping(
                source_path=Path("./docs/api"),
                target_id="id_database_documentacao_api",  # ID do database no Notion
                sync_type="bidirectional",
            ),
        ],
    )

    # Inicializar bridge
    bridge = NotionBridge(config)

    try:
        # Inicializar conexão
        await bridge.initialize()

        # Realizar primeira sincronização
        await bridge.sync()

        # Monitorar alterações continuamente
        while True:
            await asyncio.sleep(config.sync_interval)
            await bridge.sync()

    except KeyboardInterrupt:
        logging.info("Encerrando sincronização...")
    except Exception as e:
        logging.exception(f"Erro durante sincronização: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

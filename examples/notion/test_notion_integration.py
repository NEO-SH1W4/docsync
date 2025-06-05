# test_notion_integration.py
import asyncio
import logging
import os
from pathlib import Path
from docsync.integrations.notion import (
    NotionBridge,
    NotionConfig,
    NotionMapping
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_notion_connection():
    '''Teste básico de conexão com o Notion'''
    try:
        # Tentar carregar token do ambiente
        token = os.getenv('NOTION_TOKEN')
        if not token:
            logger.error('NOTION_TOKEN não encontrado nas variáveis de ambiente')
            return False

        # Criar configuração de teste
        config = NotionConfig(
            token=token,
            workspace_id='GENESIS_LAB',
            mappings=[
                NotionMapping(
                    source_path=Path('./test_docs'),
                    target_id='test_page_id'  # Será usado apenas para teste
                )
            ]
        )

        # Criar bridge
        bridge = NotionBridge(config)

        # Tentar inicializar
        logger.info('Testando conexão com Notion...')
        await bridge.initialize()
        
        logger.info('✓ Conexão estabelecida com sucesso!')
        return True

    except Exception as e:
        logger.error(f'✗ Erro ao testar conexão: {e}')
        return False

async def test_document_sync():
    '''Teste de sincronização de documento'''
    try:
        # Criar diretório e arquivo de teste
        test_dir = Path('./test_docs')
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / 'test.md'
        test_file.write_text('''# Documento de Teste
        
Este é um documento de teste para a integração DOCSYNC-Notion.

## Seção de Teste

- Item 1
- Item 2
- Item 3

## Código de Exemplo

`python
def hello_world():
    print('Hello from DOCSYNC!')
`
''')

        # Configurar Notion
        config = NotionConfig(
            token=os.getenv('NOTION_TOKEN'),
            workspace_id='GENESIS_LAB',
            mappings=[
                NotionMapping(
                    source_path=test_dir,
                    target_id=os.getenv('NOTION_TEST_PAGE_ID', 'test_page_id')
                )
            ]
        )

        # Criar bridge
        bridge = NotionBridge(config)
        await bridge.initialize()

        # Tentar sincronizar
        logger.info('Testando sincronização...')
        await bridge.sync()
        
        logger.info('✓ Sincronização concluída com sucesso!')
        return True

    except Exception as e:
        logger.error(f'✗ Erro durante sincronização: {e}')
        return False
    finally:
        # Limpar arquivos de teste
        if test_dir.exists():
            for file in test_dir.glob('*'):
                file.unlink()
            test_dir.rmdir()

async def run_all_tests():
    '''Executa todos os testes'''
    logger.info('Iniciando testes de integração com Notion...\n')

    # Teste 1: Conexão
    logger.info('=== Teste de Conexão ===')
    if await test_notion_connection():
        logger.info('✓ Teste de conexão passou!\n')
    else:
        logger.error('✗ Teste de conexão falhou!\n')
        return

    # Teste 2: Sincronização
    logger.info('=== Teste de Sincronização ===')
    if await test_document_sync():
        logger.info('✓ Teste de sincronização passou!\n')
    else:
        logger.error('✗ Teste de sincronização falhou!\n')
        return

    logger.info('=== Resumo dos Testes ===')
    logger.info('✓ Todos os testes completados com sucesso!')

if __name__ == '__main__':
    # Verificar variáveis de ambiente necessárias
    required_vars = ['NOTION_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f'Erro: Variáveis de ambiente ausentes: {", ".join(missing_vars)}')
        logger.error('Por favor, configure as variáveis de ambiente necessárias:')
        logger.error('  export NOTION_TOKEN=seu_token_aqui')
        exit(1)

    # Executar testes
    asyncio.run(run_all_tests())

# setup_notion.py
import asyncio
import click
import os
import json
from pathlib import Path
from typing import Optional
import webbrowser
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

async def validate_token(token: str) -> bool:
    '''Valida um token do Notion'''
    try:
        from docsync.integrations.notion import NotionClient, NotionConfig
        
        config = NotionConfig(token=token, workspace_id='test')
        client = NotionClient(config)
        return await client.verify_connection()
    except Exception as e:
        console.print(f'[red]Erro ao validar token: {e}[/red]')
        return False

def create_config_file(token: str, workspace_id: str, mappings: list, output_path: Path):
    '''Cria arquivo de configuração do Notion'''
    config = {
        'token': token,
        'workspace_id': workspace_id,
        'mappings': mappings,
        'sync_interval': 300,
        'max_retries': 3,
        'retry_delay': 60
    }
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)

def setup_env_file(token: str):
    '''Configura arquivo .env com credenciais'''
    env_path = Path('.env')
    content = f'NOTION_TOKEN={token}\n'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing = f.read()
        if 'NOTION_TOKEN' not in existing:
            with open(env_path, 'a') as f:
                f.write('\n' + content)
    else:
        with open(env_path, 'w') as f:
            f.write(content)

async def main():
    console.print(Panel.fit(
        '[bold blue]DOCSYNC - Configuração da Integração com Notion[/bold blue]\\n'
        'Este assistente irá ajudá-lo a configurar a integração com o Notion.'
    ))
    
    # Step 1: Token
    console.print('\\n[yellow]Passo 1: Configuração do Token[/yellow]')
    console.print('Você precisará criar uma integração no Notion e obter um token.')
    
    if Confirm.ask('Deseja abrir a página de integrações do Notion agora?'):
        webbrowser.open('https://www.notion.so/my-integrations')
        console.print('\\n[italic]Após criar a integração, copie o token e retorne aqui.[/italic]')
    
    token = Prompt.ask('\\nDigite seu token do Notion')
    
    # Validar token
    console.print('\\nValidando token...')
    if not await validate_token(token):
        console.print('[red]Token inválido! Por favor, verifique e tente novamente.[/red]')
        return
    
    console.print('[green]✓ Token válido![/green]')
    
    # Step 2: Workspace
    console.print('\\n[yellow]Passo 2: Configuração do Workspace[/yellow]')
    workspace_id = Prompt.ask('Digite o ID do seu workspace (ex: GENESIS_LAB)')
    
    # Step 3: Mapeamentos
    console.print('\\n[yellow]Passo 3: Configuração dos Mapeamentos[/yellow]')
    mappings = []
    
    while Confirm.ask('Deseja adicionar um mapeamento?', default=True):
        source = Prompt.ask('Caminho da pasta local (ex: ./docs/technical)')
        target = Prompt.ask('ID da página/database no Notion')
        sync_type = Prompt.ask(
            'Tipo de sincronização',
            choices=['bidirectional', 'push', 'pull'],
            default='bidirectional'
        )
        
        mappings.append({
            'source_path': source,
            'target_id': target,
            'sync_type': sync_type
        })
    
    # Step 4: Salvar configuração
    console.print('\\n[yellow]Passo 4: Salvando Configuração[/yellow]')
    config_path = Path('notion_config.json')
    create_config_file(token, workspace_id, mappings, config_path)
    setup_env_file(token)
    
    console.print(f'\\n[green]✓ Configuração salva em {config_path}[/green]')
    console.print('[green]✓ Variáveis de ambiente configuradas em .env[/green]')
    
    # Step 5: Instruções finais
    console.print('\\n[yellow]Próximos Passos:[/yellow]')
    console.print('''
1. Adicione .env ao seu .gitignore para proteger suas credenciais
2. Revise notion_config.json e ajuste conforme necessário
3. Execute um teste inicial:
   python examples/notion/test_notion_integration.py
4. Para sincronização contínua:
   python examples/notion/notion_sync_example.py
''')
    
    if Confirm.ask('\\nDeseja executar o teste de integração agora?'):
        console.print('\\nExecutando teste...')
        os.system('python examples/notion/test_notion_integration.py')

if __name__ == '__main__':
    asyncio.run(main())

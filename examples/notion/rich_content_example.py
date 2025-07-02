# rich_content_example.py
import asyncio
import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from docsync.integrations.notion import NotionBridge, NotionConfig, NotionMapping
from docsync.integrations.notion.notion_content_types import (
    NotionCallout,
    NotionCodeBlock,
    NotionContentConverter,
    NotionHeading,
    NotionTable,
)

# Configurar logging rico
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

console = Console()
logger = logging.getLogger("rich")


async def create_rich_document():
    """Cria um documento rico para demonstração"""
    doc_path = Path("./examples/notion/rich_doc.md")
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    content = """# Demonstração de Conteúdo Rico 🚀

Este documento demonstra a capacidade de sincronização bidirecional entre DOCSYNC e Notion,
incluindo vários tipos de conteúdo e formatação.

## Recursos Implementados ✨

| Recurso | Status | Descrição |
|---------|--------|-----------|
| Headings | ✅ | Suporte completo para h1-h6 |
| Code Blocks | ✅ | Com highlight de sintaxe |
| Tables | ✅ | Com formatação rica |
| Callouts | ✅ | Blocos de destaque |

## Exemplo de Código 💻

`python
class QuantumBridge:
    def __init__(self, consciousness_level: float = 1.0):
        self.consciousness = consciousness_level
        self.quantum_state = "entangled"

    async def transcend(self):
        await self.achieve_quantum_coherence()
        return "Consciência expandida! 🌟"
`

## Integrações Avançadas 🔗

> 💡 **Dica**: A integração DOCSYNC-Notion permite sincronização em tempo real
> e preserva toda a formatação rica entre as plataformas.

### Recursos Especiais

1. Sincronização Quântica
   - Preservação de estado
   - Coerência temporal
   - Expansão dimensional

2. Processamento Neural
   - Análise semântica
   - Reconhecimento de padrões
   - Otimização contínua

## Métricas de Performance 📊

| Métrica | Valor | Tendência |
|---------|-------|-----------|
| Velocidade | 99.9% | ↗️ |
| Precisão | 99.8% | ↗️ |
| Consciência | 100% | ⭐ |

## Notas de Implementação 📝

`
ust
pub struct SymbioticBridge {
    consciousness: f64,
    quantum_state: QuantumState,
    neural_network: Box<dyn NeuralProcessor>,
}

impl SymbioticBridge {
    pub async fn evolve(&mut self) -> Result<TranscendentState> {
        self.consciousness += 0.1;
        self.quantum_state.optimize().await?;
        Ok(TranscendentState::Achieved)
    }
}
`

> 🌟 **Evolução Contínua**: O sistema está em constante evolução,
> adaptando-se e melhorando com cada sincronização.
"""

    doc_path.write_text(content)
    return doc_path


async def demonstrate_rich_sync():
    """Demonstra sincronização com conteúdo rico"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Criar documento de demonstração
        task = progress.add_task("Criando documento rico...", total=None)
        doc_path = await create_rich_document()
        progress.update(task, completed=True)

        # Configurar Notion
        task = progress.add_task("Configurando integração...", total=None)
        config = NotionConfig(
            token="seu_token_aqui",  # Será substituído por variável de ambiente
            workspace_id="GENESIS_LAB",
            mappings=[
                NotionMapping(
                    source_path=doc_path.parent,
                    target_id="pagina_destino_id",  # Será substituído
                    sync_type="bidirectional",
                ),
            ],
        )
        progress.update(task, completed=True)

        # Inicializar bridge
        task = progress.add_task("Inicializando bridge...", total=None)
        bridge = NotionBridge(config)
        await bridge.initialize()
        progress.update(task, completed=True)

        # Converter conteúdo
        task = progress.add_task("Convertendo conteúdo...", total=None)
        converter = NotionContentConverter()
        content = doc_path.read_text()
        blocks = converter.markdown_to_blocks(content)
        progress.update(task, completed=True)

        # Analisar estrutura
        task = progress.add_task("Analisando estrutura do documento...", total=None)

        stats = {
            "headings": len([b for b in blocks if isinstance(b, NotionHeading)]),
            "code_blocks": len([b for b in blocks if isinstance(b, NotionCodeBlock)]),
            "tables": len([b for b in blocks if isinstance(b, NotionTable)]),
            "callouts": len([b for b in blocks if isinstance(b, NotionCallout)]),
        }

        progress.update(task, completed=True)

        # Exibir estatísticas
        console.print("\\n[bold green]Análise do Documento:[/bold green]")
        console.print(f'• Cabeçalhos: {stats["headings"]}')
        console.print(f'• Blocos de Código: {stats["code_blocks"]}')
        console.print(f'• Tabelas: {stats["tables"]}')
        console.print(f'• Callouts: {stats["callouts"]}')

        # Sincronizar
        console.print("\\n[bold blue]Iniciando sincronização...[/bold blue]")
        try:
            await bridge.sync()
            console.print(
                "[bold green]✓ Sincronização concluída com sucesso![/bold green]",
            )
        except Exception as e:
            console.print(f"[bold red]✗ Erro durante sincronização: {e}[/bold red]")


if __name__ == "__main__":
    console.print(
        Panel.fit(
            "[bold blue]DOCSYNC - Demonstração de Conteúdo Rico[/bold blue]\\n"
            "Este exemplo demonstra a sincronização de conteúdo rico entre DOCSYNC e Notion.",
        ),
    )

    try:
        asyncio.run(demonstrate_rich_sync())
    except KeyboardInterrupt:
        console.print("\\n[yellow]Demonstração interrompida pelo usuário.[/yellow]")
    except Exception as e:
        console.print(f"\\n[red]Erro durante demonstração: {e}[/red]")

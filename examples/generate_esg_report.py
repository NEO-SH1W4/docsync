"""
Exemplo de geração de relatório ESG usando o DocSync.

Este script demonstra a geração de relatórios ESG com:
- Dados estruturados de métricas ESG
- Formatação avançada
- Feedback visual do processo
- Tratamento de erros
"""

import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from docsync.core import DocumentSynchronizer
from docsync.exceptions import DocSyncError

# Inicializa console rich para feedback visual
console = Console()


def generate_esg_data():
    """Gera dados de exemplo para o relatório ESG."""
    return {
        "metrics": [
            {
                "category": "ambiental",
                "name": "Emissão de CO2",
                "value": 125.5,
                "unit": "ton",
                "target": "100 ton",
                "status": "at_risk",
                "trend": "↗️",
            },
            {
                "category": "ambiental",
                "name": "Consumo de Energia",
                "value": 450.75,
                "unit": "kWh",
                "target": "400 kWh",
                "status": "in_progress",
                "trend": "➡️",
            },
            {
                "category": "social",
                "name": "Satisfação dos Funcionários",
                "value": 85,
                "unit": "%",
                "target": "90%",
                "status": "on_track",
                "trend": "↗️",
            },
        ],
        "objectives": [
            {
                "title": "Redução de Emissões",
                "description": "Reduzir emissões de CO2 em 20% até 2024",
                "progress": 65,
                "status": "in_progress",
            },
            {
                "title": "Eficiência Energética",
                "description": "Implementar medidas de economia de energia",
                "progress": 80,
                "status": "on_track",
            },
        ],
        "analysis": {
            "Impacto Ambiental": {
                "summary": "Análise detalhada das iniciativas ambientais.",
                "key_points": [
                    "Redução significativa no consumo de energia",
                    "Implementação de programa de reciclagem",
                ],
                "challenges": [
                    "Aumento nas emissões de CO2 devido ao crescimento",
                    "Adaptação a novas regulamentações",
                ],
                "opportunities": [
                    "Investimento em energia renovável",
                    "Otimização da cadeia logística",
                ],
            },
        },
        "recommendations": [
            {
                "title": "Otimização Energética",
                "description": "Implementar sistema de monitoramento.",
                "priority": "Alta",
                "impact": "Significativo",
                "timeline": "Q2 2024",
            },
            {
                "title": "Programa de Compensação",
                "description": "Desenvolver programa de compensação de carbono.",
                "priority": "Média",
                "impact": "Moderado",
                "timeline": "Q3 2024",
            },
        ],
    }


def main():
    """Função principal do exemplo."""
    try:
        # Configura caminhos
        base_path = Path(__file__).parent.parent
        templates_path = base_path / "src" / "docsync" / "templates"
        output_path = base_path / "reports"
        output_path.mkdir(exist_ok=True)

        # Apresenta cabeçalho
        console.print(
            Panel.fit("🌿 Gerador de Relatório ESG - GUARDRIVE", style="green"),
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Inicializa DocumentSynchronizer
            task = progress.add_task(
                "Inicializando Document Synchronizer...",
                total=None,
            )
            doc_sync = DocumentSynchronizer(
                base_path=base_path,
                templates_path=templates_path,
            )
            progress.update(task, completed=True)

            # Prepara dados
            task = progress.add_task("Preparando dados do relatório...", total=None)
            report_data = generate_esg_data()
            progress.update(task, completed=True)

            # Gera relatório
            task = progress.add_task("Gerando relatório ESG...", total=None)
            report_config = {
                "title": "Relatório ESG GUARDRIVE Q1 2024",
                "period": "Q1 2024",
                "metrics": report_data["metrics"],
                "objectives": report_data["objectives"],
                "analysis": report_data["analysis"],
                "recommendations": report_data["recommendations"],
                "overview": "Relatório trimestral de métricas ESG.",
                "version": "1.0.0",
                "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }

            output_file = output_path / "esg_q1_2024.md"
            doc_sync.generate_report(
                template_name="guardrive/esg_report",
                output_path=output_file,
                data=report_config,
            )
            progress.update(task, completed=True)

        # Apresenta resumo
        console.print("\n✨ Relatório gerado com sucesso!", style="green")
        console.print(f"\n📝 Arquivo gerado: {output_file}", style="blue")

    except DocSyncError as e:
        console.print(f"\n❌ Erro ao gerar relatório: {e!s}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {e!s}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()

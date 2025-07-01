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
                "trend": "↗️"
            },
            {
                "category": "ambiental",
                "name": "Consumo de Energia",
                "value": 450.75,
                "unit": "kWh",
                "target": "400 kWh",
                "status": "in_progress",
                "trend": "➡️"
            },
            {
                "category": "social",
                "name": "Satisfação dos Funcionários",
                "value": 85,
                "unit": "%",
                "target": "90%",
                "status": "on_track",
                "trend": "↗️"
            }
        ],
        "objectives": [
            {
                "title": "Redução de Emissões",
                "description": "Reduzir emissões de CO2 em 20% até 2024",
                "progress": 65,
                "status": "in_progress"
            },
            {
                "title": "Eficiência Energética",
                "description": "Implementar medidas de economia de energia",
                "progress": 80,
                "status": "on_track"
            }
        ],
        "analysis": {
            "Impacto Ambiental": {
                "summary": "Análise detalhada das iniciativas ambientais e seus resultados.",
                "key_points": [
                    "Redução significativa no consumo de energia",
                    "Implementação de programa de reciclagem"
                ],
                "challenges": [
                    "Aumento nas emissões de CO2 devido ao crescimento",
                    "Adaptação a novas regulamentações"
                ],
                "opportunities": [
                    "Investimento em energia renovável",
                    "Otimização da cadeia logística"
                ]
            }
        },
        "recommendations": [
            {
                "title": "Otimização Energética",
                "description": "Implementar sistema de monitoramento em tempo real do consumo de energia.",
                "priority": "Alta",
                "impact": "Significativo",
                "timeline": "Q2 2024"
            },
            {
                "title": "Programa de Compensação",
                "description": "Desenvolver programa de compensação de carbono.",
                "priority": "Média",
                "impact": "Moderado",
                "timeline": "Q3 2024"
            }
        ]
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
        console.print(Panel.fit(
            "🌿 Gerador de Relatório ESG - GUARDRIVE",
            style="green"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Inicializa DocumentSynchronizer
            task = progress.add_task("Inicializando Document Synchronizer...", total=None)
            doc_sync = DocumentSynchronizer(
                base_path=base_path,
                templates_path=templates_path
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
                "overview": "Relatório trimestral de métricas ESG e progresso das iniciativas.",
                "version": "1.0.0",
                "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            output_file = output_path / "esg_q1_2024.md"
            doc_sync.generate_report(
                template_name="guardrive/esg_report",
                output_path=output_file,
                data=report_config
            )
            progress.update(task, completed=True)

        # Apresenta resumo
        console.print("\n✨ Relatório gerado com sucesso!", style="green")
        console.print(f"\n📝 Arquivo gerado: {output_file}", style="blue")

    except DocSyncError as e:
        console.print(f"\n❌ Erro ao gerar relatório: {str(e)}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Exemplo de geração de relatório ESG usando o DocSync.

Este script demonstra a geração de relatórios ESG com:
- Dados estruturados de métricas ESG
- Formatação avançada
- Exportação para múltiplos formatos
- Feedback visual do processo
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

def generate_sample_data():
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
                "trend": "↗️"
            },
            {
                "category": "ambiental",
                "name": "Consumo de Energia",
                "value": 450.75,
                "unit": "kWh",
                "target": "400 kWh",
                "status": "in_progress",
                "trend": "➡️"
            },
            {
                "category": "social",
                "name": "Satisfação dos Funcionários",
                "value": 85,
                "unit": "%",
                "target": "90%",
                "status": "on_track",
                "trend": "↗️"
            }
        ],
        "objectives": [
            {
                "title": "Redução de Emissões",
                "description": "Reduzir emissões de CO2 em 20% até 2024",
                "progress": 65,
                "status": "in_progress"
            },
            {
                "title": "Eficiência Energética",
                "description": "Implementar medidas de economia de energia",
                "progress": 80,
                "status": "on_track"
            }
        ],
        "analysis": {
            "Impacto Ambiental": {
                "summary": "Análise detalhada das iniciativas ambientais e seus resultados.",
                "key_points": [
                    "Redução significativa no consumo de energia",
                    "Implementação de programa de reciclagem"
                ],
                "challenges": [
                    "Aumento nas emissões de CO2 devido ao crescimento",
                    "Adaptação a novas regulamentações"
                ],
                "opportunities": [
                    "Investimento em energia renovável",
                    "Otimização da cadeia logística"
                ]
            }
        },
        "recommendations": [
            {
                "title": "Otimização Energética",
                "description": "Implementar sistema de monitoramento em tempo real do consumo de energia.",
                "priority": "Alta",
                "impact": "Significativo",
                "timeline": "Q2 2024"
            },
            {
                "title": "Programa de Compensação",
                "description": "Desenvolver programa de compensação de carbono.",
                "priority": "Média",
                "impact": "Moderado",
                "timeline": "Q3 2024"
            }
        ]
    }

def main():
    # Dados de exemplo para o relatório
    metrics = [
        {
            "name": "Emissão de CO2",
            "value": 1250.5,
            "unit": "ton",
            "target": {"value": 1000, "unit": "ton"},
            "status": "at_risk",
            "category": "environmental"
        },
        {
            "name": "Consumo de Energia",
            "value": 45000,
            "unit": "kwh",
            "target": {"value": 40000, "unit": "kwh"},
            "status": "delayed",
            "category": "environmental"
        },
        {
            "name": "Diversidade na Liderança",
            "value": 35,
            "unit": "%",
            "target": {"value": 50, "unit": "%"},
            "status": "in_progress",
            "category": "social"
        },
        {
            "name": "Compliance Score",
            "value": 95,
            "unit": "%",
            "target": {"value": 100, "unit": "%"},
            "status": "on_track",
            "category": "governance"
        }
    ]

    objectives = [
        {
            "title": "Redução de Emissões",
            "description": "Reduzir emissões de CO2 em 20% até 2025",
            "progress": {"value": 35, "unit": "%"},
            "status": "in_progress",
            "milestones": [
                {"description": "Auditoria de Emissões", "status": "completed"},
                {"description": "Implementação de Filtros", "status": "in_progress"},
                {"description": "Certificação ISO", "status": "pending"}
            ]
        }
    ]

    analysis = {
        "environmental": {
            "summary": "Progresso significativo na redução de impacto ambiental.",
            "key_points": [
                "Redução de 15% no consumo de energia",
                "Implementação de sistema de reciclagem"
            ],
            "challenges": [
                "Alto custo de equipamentos sustentáveis",
                "Adaptação da equipe a novos processos"
            ]
        }
    }

    recommendations = [
        {
            "title": "Expansão do Programa de Reciclagem",
            "description": "Ampliar o programa de reciclagem para todas as unidades.",
            "priority": "high",
            "timeline": "Q3 2024",
            "steps": [
                "Avaliar infraestrutura atual",
                "Treinar equipes locais",
                "Implementar pontos de coleta"
            ]
        }
    ]

    # Gera o relatório
    report_path = Path("reports/esg_report_q1_2024.md")
    
    try:
        generate_esg_report(
            title="Relatório ESG GUARDRIVE - Q1 2024",
            period="Q1 2024",
            metrics=metrics,
            objectives=objectives,
            analysis=analysis,
            recommendations=recommendations,
            target_path=report_path,
            overview="Análise trimestral de indicadores ESG do GUARDRIVE.",
            version="1.0.0"
        )
        print(f"Relatório gerado com sucesso: {report_path}")
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")

if __name__ == "__main__":
    main()

"""
Exemplo de geração de relatório ESG usando DocSync.
"""

from pathlib import Path

from docsync.core import DocSync


def main():
    try:
        # Configura caminhos
        base_path = Path(__file__).parent.parent
        templates_path = base_path / "src" / "docsync" / "templates"
        output_path = base_path / "reports"
        output_path.mkdir(exist_ok=True)

        # Apresenta cabeçalho
        console.print(Panel.fit(
            "🌿 Gerador de Relatório ESG - GUARDRIVE",
            style="green"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Inicializa DocumentSynchronizer
            task = progress.add_task("Inicializando Document Synchronizer...", total=None)
            doc_sync = DocumentSynchronizer(
                templates_path=templates_path,
                config_path=None,
                log_level="INFO"
            )
            progress.update(task, completed=True)

            # Prepara dados
            task = progress.add_task("Preparando dados do relatório...", total=None)
            report_data = generate_sample_data()
            progress.update(task, completed=True)

            # Gera relatório
            task = progress.add_task("Gerando relatório ESG...", total=None)
    metrics = [
        {
            "category": "ambiental",
            "name": "Emissão de CO2",
            "value": 125.5,
            "unit": "ton",
            "target": "100 ton",
            "status": "at_risk",
            "trend": "↗️"
        },
        {
            "category": "ambiental",
            "name": "Consumo de Energia",
            "value": 450.75,
            "unit": "kWh",
            "target": "400 kWh",
            "status": "in_progress",
            "trend": "➡️"
        },
        {
            "category": "social",
            "name": "Satisfação dos Funcionários",
            "value": 85,
            "unit": "%",
            "target": "90%",
            "status": "on_track",
            "trend": "↗️"
        }
    ]
    
    objectives = [
        {
            "title": "Redução de Emissões",
            "description": "Reduzir emissões de CO2 em 20% até 2024",
            "progress": 65,
            "status": "in_progress"
        },
        {
            "title": "Eficiência Energética",
            "description": "Implementar medidas de economia de energia",
            "progress": 80,
            "status": "on_track"
        }
    ]
    
    analysis = {
        "Impacto Ambiental": {
            "summary": "Análise detalhada das iniciativas ambientais e seus resultados.",
            "key_points": [
                "Redução significativa no consumo de energia",
                "Implementação de programa de reciclagem"
            ],
            "challenges": [
                "Aumento nas emissões de CO2 devido ao crescimento",
                "Adaptação a novas regulamentações"
            ],
            "opportunities": [
                "Investimento em energia renovável",
                "Otimização da cadeia logística"
            ]
        }
    }
    
    recommendations = [
        {
            "title": "Otimização Energética",
            "description": "Implementar sistema de monitoramento em tempo real do consumo de energia.",
            "priority": "Alta",
            "impact": "Significativo",
            "timeline": "Q2 2024"
        },
        {
            "title": "Programa de Compensação",
            "description": "Desenvolver programa de compensação de carbono.",
            "priority": "Média",
            "impact": "Moderado",
            "timeline": "Q3 2024"
        }
    ]
    
            # Prepara dados do relatório
            report_config = {
                "title": "Relatório ESG GUARDRIVE Q1 2024",
                "period": "Q1 2024",
                "metrics": report_data["metrics"],
                "objectives": report_data["objectives"],
                "analysis": report_data["analysis"],
                "recommendations": report_data["recommendations"],
                "overview": "Relatório trimestral de métricas ESG e progresso das iniciativas.",
                "version": "1.0.0",
                "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # Gera relatórios em diferentes formatos
            md_path = output_path / "esg_q1_2024.md"
            html_path = output_path / "esg_q1_2024.html"

            # Markdown
            doc_sync.create_document(
                template_name="guardrive/esg_report",
                target_path=str(md_path),
                data=report_config
            )

            # HTML
            doc_sync.create_document(
                template_name="guardrive/esg_report",
                target_path=str(html_path),
                data=report_config,
                format="html"
            )

            progress.update(task, completed=True)

        # Apresenta resumo
        console.print("\n✨ Relatório gerado com sucesso!", style="green")
        console.print("\nArquivos gerados:")
        console.print(f"📝 Markdown: {md_path}")
        console.print(f"🌐 HTML: {html_path}")

    except DocSyncError as e:
        console.print(f"\n❌ Erro ao gerar relatório: {str(e)}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()


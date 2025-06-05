"""
Testes unitários para funcionalidade de geração de relatórios ESG.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from docsync.core import DocumentSynchronizer
from docsync.exceptions import DocSyncError

# Fixtures

@pytest.fixture
def sample_metrics():
    """Retorna métricas ESG de exemplo."""
    return [
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
            "category": "social",
            "name": "Satisfação dos Funcionários",
            "value": 85,
            "unit": "%",
            "target": "90%",
            "status": "on_track",
            "trend": "↗️"
        }
    ]

@pytest.fixture
def sample_objectives():
    """Retorna objetivos ESG de exemplo."""
    return [
        {
            "title": "Redução de Emissões",
            "description": "Reduzir emissões de CO2 em 20% até 2024",
            "progress": 65,
            "status": "in_progress"
        }
    ]

@pytest.fixture
def sample_analysis():
    """Retorna análise ESG de exemplo."""
    return {
        "Impacto Ambiental": {
            "summary": "Análise detalhada das iniciativas ambientais.",
            "key_points": ["Redução no consumo de energia"],
            "challenges": ["Aumento nas emissões"],
            "opportunities": ["Energia renovável"]
        }
    }

@pytest.fixture
def sample_recommendations():
    """Retorna recomendações ESG de exemplo."""
    return [
        {
            "title": "Otimização Energética",
            "description": "Implementar monitoramento em tempo real.",
            "priority": "Alta",
            "impact": "Significativo",
            "timeline": "Q2 2024"
        }
    ]

@pytest.fixture
def mock_doc_sync():
    """Retorna um DocumentSynchronizer mockado."""
    with patch("docsync.core.DocumentSynchronizer") as mock:
        synchronizer = mock.return_value
        synchronizer.generate_report.return_value = Path("output/report.md")
        yield synchronizer

# Testes

def test_metrics_structure(sample_metrics):
    """Testa estrutura das métricas ESG."""
    for metric in sample_metrics:
        assert "category" in metric
        assert "name" in metric
        assert "value" in metric
        assert "unit" in metric
        assert "target" in metric
        assert "status" in metric
        assert "trend" in metric

def test_objectives_structure(sample_objectives):
    """Testa estrutura dos objetivos ESG."""
    for objective in sample_objectives:
        assert "title" in objective
        assert "description" in objective
        assert "progress" in objective
        assert "status" in objective
        assert 0 <= objective["progress"] <= 100

def test_analysis_structure(sample_analysis):
    """Testa estrutura da análise ESG."""
    for category, data in sample_analysis.items():
        assert "summary" in data
        assert "key_points" in data
        assert "challenges" in data
        assert "opportunities" in data
        assert all(isinstance(x, list) for x in [
            data["key_points"],
            data["challenges"],
            data["opportunities"]
        ])

def test_recommendations_structure(sample_recommendations):
    """Testa estrutura das recomendações ESG."""
    for rec in sample_recommendations:
        assert "title" in rec
        assert "description" in rec
        assert "priority" in rec
        assert "impact" in rec
        assert "timeline" in rec

def test_report_generation_markdown(mock_doc_sync, sample_metrics, sample_objectives):
    """Testa geração de relatório em Markdown."""
    config = {
        "title": "Relatório ESG Teste",
        "period": "Q1 2024",
        "metrics": sample_metrics,
        "objectives": sample_objectives,
        "version": "1.0.0"
    }
    
    result = mock_doc_sync.generate_report(
        template_name="guardrive/esg_report",
        output_path="output/report.md",
        data=config
    )
    
    assert result.exists()
    mock_doc_sync.generate_report.assert_called_once()

def test_report_generation_html(mock_doc_sync, sample_metrics, sample_objectives):
    """Testa geração de relatório em HTML."""
    config = {
        "title": "Relatório ESG Teste",
        "period": "Q1 2024",
        "metrics": sample_metrics,
        "objectives": sample_objectives,
        "version": "1.0.0"
    }
    
    result = mock_doc_sync.generate_report(
        template_name="guardrive/esg_report",
        output_path="output/report.html",
        data=config,
        format="html"
    )
    
    assert result.exists()
    mock_doc_sync.generate_report.assert_called_once()

def test_error_handling_invalid_template(mock_doc_sync):
    """Testa tratamento de erro para template inválido."""
    mock_doc_sync.generate_report.side_effect = DocSyncError("Template não encontrado")
    
    with pytest.raises(DocSyncError) as exc:
        mock_doc_sync.generate_report(
            template_name="invalid/template",
            output_path="output/report.md",
            data={}
        )
    
    assert "Template não encontrado" in str(exc.value)

def test_path_resolution():
    """Testa resolução de caminhos do projeto."""
    base_path = Path(__file__).parent.parent
    templates_path = base_path / "src" / "docsync" / "templates"
    output_path = base_path / "reports"
    
    assert templates_path.exists()
    assert "guardrive" in [p.name for p in templates_path.iterdir()]

@pytest.mark.integration
def test_full_report_generation():
    """Teste de integração para geração completa do relatório."""
    # Este teste requer ambiente completo configurado
    templates_path = Path(__file__).parent.parent / "src" / "docsync" / "templates"
    output_path = Path(__file__).parent / "output"
    output_path.mkdir(exist_ok=True)
    
    doc_sync = DocumentSynchronizer(templates_path=templates_path)
    
    config = {
        "title": "Relatório ESG Integração",
        "period": "Q1 2024",
        "metrics": [
            {
                "category": "ambiental",
                "name": "Emissão de CO2",
                "value": 125.5,
                "unit": "ton",
                "target": "100 ton",
                "status": "at_risk",
                "trend": "↗️"
            }
        ],
        "objectives": [
            {
                "title": "Redução de Emissões",
                "description": "Reduzir emissões de CO2",
                "progress": 65,
                "status": "in_progress"
            }
        ],
        "version": "1.0.0",
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    # Gera relatório nos dois formatos
    md_path = output_path / "integration_test.md"
    html_path = output_path / "integration_test.html"
    
    assert doc_sync.generate_report(
        template_name="guardrive/esg_report",
        output_path=str(md_path),
        data=config
    )
    
    assert doc_sync.generate_report(
        template_name="guardrive/esg_report",
        output_path=str(html_path),
        data=config,
        format="html"
    )
    
    assert md_path.exists()
    assert html_path.exists()

def test_console_output():
    """Testa saída visual no console."""
    console = Console()
    
    with console.capture() as capture:
        console.print("✨ Relatório gerado com sucesso!", style="green")
        console.print("📝 Markdown: output/report.md", style="blue")
    
    output = capture.get()
    assert "✨" in output
    assert "📝" in output
    assert "report.md" in output


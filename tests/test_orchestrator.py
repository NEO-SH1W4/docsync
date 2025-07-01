"""
Testes para o orquestrador de templates.
"""

from pathlib import Path

import pytest

from docsync.exceptions import OrchestratorError, TemplateError
from docsync.templates.orchestrator import TemplateConfig, TemplateOrchestrator


@pytest.fixture
def template_dir(tmp_path):
    """Cria estrutura de templates para teste."""
    sections = tmp_path / "guardrive" / "sections"
    sections.mkdir(parents=True)

    # Cria templates de teste
    (sections / "test_section.md.jinja").write_text("# {{ title }}")
    (sections / "test_section.html.jinja").write_text("<h1>{{ title }}</h1>")

    return tmp_path


@pytest.fixture
def orchestrator(template_dir):
    """Cria instância do orquestrador para teste."""
    return TemplateOrchestrator(template_dir)


def test_load_invalid_config(orchestrator):
    """Testa carregamento de configuração inválida."""
    config = TemplateConfig(
        name="",
        sections=[],
        format="invalid",
        metadata={},
        data={},
        output_path=Path("test.md"),
    )

    with pytest.raises(OrchestratorError):
        orchestrator._validate_template_config(config)


def test_generate_markdown_report(orchestrator, tmp_path):
    """Testa geração de relatório markdown."""
    config = TemplateConfig(
        name="test",
        sections=["test_section"],
        format="md",
        metadata={},
        data={"title": "Test Report"},
        output_path=tmp_path / "report.md",
    )

    output = orchestrator.generate_report(config)
    assert output.exists()
    assert output.read_text() == "# Test Report"


def test_generate_html_report(orchestrator, tmp_path):
    """Testa geração de relatório HTML."""
    config = TemplateConfig(
        name="test",
        sections=["test_section"],
        format="html",
        metadata={},
        data={"title": "Test Report"},
        output_path=tmp_path / "report.html",
    )

    output = orchestrator.generate_report(config)
    assert output.exists()
    assert output.read_text() == "<h1>Test Report</h1>"


def test_missing_template(orchestrator, tmp_path):
    """Testa erro com template inexistente."""
    config = TemplateConfig(
        name="test",
        sections=["missing_section"],
        format="md",
        metadata={},
        data={"title": "Test"},
        output_path=tmp_path / "report.md",
    )

    with pytest.raises(TemplateError):
        orchestrator.generate_report(config)


def test_list_templates(orchestrator, template_dir):
    """Testa listagem de templates disponíveis."""
    templates = orchestrator.list_templates()
    assert "test_section" in templates["sections"]

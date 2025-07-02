"""
Testes para o sistema de filtros do DocSync.
"""

from datetime import datetime

import pytest
from jinja2 import Environment

from docsync.utils.filter_registry import FilterRegistry


@pytest.fixture
def filter_registry():
    """Fixture que fornece um FilterRegistry configurado."""
    registry = FilterRegistry()
    env = Environment()
    registry.setup_environment(env)
    return registry


def test_format_metric():
    """Testa formatação de métricas com diferentes unidades."""
    registry = FilterRegistry()

    # Teste com toneladas
    assert registry.format_metric(1234.5678, "ton") == "1,234.57 ton"

    # Teste com percentual
    assert registry.format_metric(42.5, "%") == "42.5%"
    assert registry.format_metric(42.5, "percent") == "42.5%"

    # Teste com kWh
    assert registry.format_metric(9876.54, "kWh") == "9,876.54 kWh"

    # Teste com outras unidades
    assert registry.format_metric(123.45, "m³") == "123.45 m³"

    # Teste com valor nulo
    assert registry.format_metric(None, "ton") == "N/A"

    # Teste com valor zero
    assert registry.format_metric(0, "%") == "0.0%"


def test_format_status():
    """Testa formatação de status com emojis."""
    registry = FilterRegistry()

    # Testa diferentes status
    assert "✅" in registry.format_status("completed")
    assert "🔄" in registry.format_status("in_progress")
    assert "⏳" in registry.format_status("pending")
    assert "⚠️" in registry.format_status("delayed")
    assert "✅" in registry.format_status("on_track")
    assert "⚠️" in registry.format_status("at_risk")
    assert "❌" in registry.format_status("off_track")

    # Testa status desconhecido
    assert registry.format_status("unknown") == "unknown"

    # Testa case sensitivity
    assert "✅" in registry.format_status("COMPLETED")
    assert "🔄" in registry.format_status("In_Progress")


def test_format_priority():
    """Testa formatação de prioridades."""
    registry = FilterRegistry()

    # Testa diferentes prioridades
    assert "🔴" in registry.format_priority("high")
    assert "🟡" in registry.format_priority("medium")
    assert "🟢" in registry.format_priority("low")

    # Testa prioridade desconhecida
    assert registry.format_priority("unknown") == "unknown"

    # Testa case sensitivity
    assert "🔴" in registry.format_priority("HIGH")
    assert "🟡" in registry.format_priority("Medium")


def test_format_date():
    """Testa formatação de datas."""
    registry = FilterRegistry()

    # Testa data comum
    date = datetime(2024, 1, 15, 14, 30)
    assert registry.format_date(date) == "15/01/2024"

    # Testa data com tempo
    assert registry.format_date(date, with_time=True) == "15/01/2024 14:30"

    # Testa data nula
    assert registry.format_date(None) == "N/A"

    # Testa formato personalizado
    assert registry.format_date(date, fmt="%Y-%m-%d") == "2024-01-15"


def test_format_progress():
    """Testa formatação de barras de progresso."""
    registry = FilterRegistry()

    # Testa diferentes percentuais
    assert "##########" in registry.format_progress(100)  # Completo
    assert "#####....." in registry.format_progress(50)  # Metade
    assert "......" in registry.format_progress(0)  # Vazio

    # Testa valores inválidos
    assert registry.format_progress(-10) == "[E]"  # Negativo
    assert registry.format_progress(110) == "[E]"  # Acima de 100
    assert registry.format_progress(None) == "[E]"  # Nulo


def test_format_trend():
    """Testa formatação de tendências."""
    registry = FilterRegistry()

    # Testa diferentes tendências
    assert "↗️" in registry.format_trend("increasing")
    assert "↘️" in registry.format_trend("decreasing")
    assert "➡️" in registry.format_trend("stable")

    # Testa tendência desconhecida
    assert registry.format_trend("unknown") == "➡️"

    # Testa case sensitivity
    assert "↗️" in registry.format_trend("INCREASING")
    assert "↘️" in registry.format_trend("Decreasing")


def test_custom_filters():
    """Testa registro e uso de filtros customizados."""
    registry = FilterRegistry()
    env = Environment()

    # Registra filtro customizado
    @registry.register_filter
    def double(value):
        """Dobra o valor numérico."""
        try:
            return float(value) * 2
        except (ValueError, TypeError):
            return value

    # Configura ambiente
    registry.setup_environment(env)

    # Verifica se filtro foi registrado
    assert "double" in env.filters
    assert env.filters["double"](5) == 10.0
    assert env.filters["double"]("invalid") == "invalid"


def test_filter_chain():
    """Testa encadeamento de filtros."""
    registry = FilterRegistry()
    env = Environment()
    registry.setup_environment(env)

    # Cria template que encadeia filtros
    template = env.from_string("{{ value | format_metric('ton') | upper }}")

    # Testa renderização
    assert template.render(value=1234.56) == "1,234.56 TON"


def test_filter_context():
    """Testa filtros que dependem de contexto."""
    registry = FilterRegistry()
    env = Environment()
    registry.setup_environment(env)

    # Cria template que usa contexto
    template = env.from_string(
        """
    {% set ctx = {'unit': 'ton'} %}
    {{ value | format_with_context(ctx) }}
    """,
    )

    # Testa renderização
    assert "1,234.56 ton" in template.render(value=1234.56)

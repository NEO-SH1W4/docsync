"""Filtros personalizados para templates Jinja2."""

from datetime import datetime
from typing import Any, Optional


def format_status(status: str) -> str:
    """Formata o status para exibição."""
    status_map = {
        "completed": "Concluído",
        "in_progress": "Em Andamento",
        "pending": "Pendente",
        "delayed": "Atrasado",
        "cancelled": "Cancelado",
        "on_track": "No Prazo",
        "at_risk": "Em Risco",
        "blocked": "Bloqueado",
    }
    return status_map.get(status.lower(), status)


def status_class(status: str) -> str:
    """Retorna a classe CSS apropriada para o status."""
    class_map = {
        "completed": "bg-success",
        "in_progress": "bg-primary",
        "pending": "bg-warning",
        "delayed": "bg-danger",
        "cancelled": "bg-secondary",
        "on_track": "bg-success",
        "at_risk": "bg-warning",
        "blocked": "bg-danger",
    }
    return class_map.get(status.lower(), "bg-secondary")


def format_metric(value: Any, metric_type: str, unit: Optional[str] = None) -> str:
    """Formata valor de métrica com base no tipo e unidade."""
    if metric_type == "percentage":
        return f"{float(value):.1f}%"
    if metric_type == "currency":
        return f"R$ {float(value):,.2f}"
    if metric_type == "number":
        return f"{float(value):,.0f}"
    if metric_type == "decimal":
        return f"{float(value):,.2f}"

    formatted = str(value)
    if unit:
        formatted = f"{formatted} {unit}"
    return formatted


def format_date(date: datetime) -> str:
    """Formata data para o padrão brasileiro."""
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        except ValueError:
            return date

    return date.strftime("%d/%m/%Y")


def format_version(version: str) -> str:
    """Formata número de versão."""
    if not version:
        return "1.0.0"
    return str(version)


def format_trend(trend: str, previous_value: Optional[float] = None) -> str:
    """Formata indicador de tendência."""
    trend_map = {
        "up": '<i class="fas fa-arrow-up text-success"></i>',
        "down": '<i class="fas fa-arrow-down text-danger"></i>',
        "stable": '<i class="fas fa-equals text-warning"></i>',
        "increasing": '<i class="fas fa-arrow-up text-success"></i>',
        "decreasing": '<i class="fas fa-arrow-down text-danger"></i>',
        "neutral": '<i class="fas fa-equals text-warning"></i>',
    }

    if previous_value is not None and isinstance(previous_value, (int, float)):
        return trend_map.get(trend.lower(), trend)
    return ""


def priority_class(priority: str) -> str:
    """Retorna classe CSS para prioridade."""
    class_map = {
        "high": "priority-high",
        "medium": "priority-medium",
        "low": "priority-low",
        "alta": "priority-high",
        "média": "priority-medium",
        "baixa": "priority-low",
    }
    return class_map.get(priority.lower(), "priority-medium")


# Registra todos os filtros disponíveis
FILTERS = {
    "format_status": format_status,
    "status_class": status_class,
    "format_metric": format_metric,
    "format_date": format_date,
    "format_version": format_version,
    "format_trend": format_trend,
    "priority_class": priority_class,
}

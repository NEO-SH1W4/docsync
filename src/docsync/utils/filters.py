"""
Custom Jinja2 filters for template rendering.
"""

from datetime import datetime
from typing import Any, Optional, Union


def format_metric(value: Any, metric_type: str, unit: Optional[str] = None) -> str:
    """
    Format a metric value based on its type and unit.

    Args:
        value: The metric value to format
        metric_type: Type of metric (percentage, currency, number, etc)
        unit: Optional unit to append

    Returns:
        Formatted metric string
    """
    if not value:
        return "N/A"

    try:
        if metric_type == "percentage":
            formatted = f"{float(value):.1f}%"
        elif metric_type == "currency":
            formatted = f"R$ {float(value):,.2f}"
        elif metric_type == "number":
            formatted = f"{float(value):,.2f}"
        else:
            formatted = str(value)

        if unit and metric_type not in ("percentage", "currency"):
            formatted = f"{formatted} {unit}"

        return formatted
    except (ValueError, TypeError):
        return str(value)


def to_percentage(value: float) -> str:
    """Convert decimal to percentage string."""
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_date(value: Union[str, datetime], format_str: str = "%d/%m/%Y") -> str:
    """Format date string to dd/mm/yyyy."""
    if not value:
        return ""

    if isinstance(value, str):
        try:
            # Try different formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                try:
                    date_obj = datetime.strptime(value, fmt)
                    return date_obj.strftime(format_str)
                except ValueError:
                    continue
        except Exception:
            return value
    elif isinstance(value, datetime):
        return value.strftime(format_str)

    return str(value)


def format_status(value: str) -> str:
    """Format status with emojis."""
    status_map = {
        "on_track": "✅ No prazo",
        "at_risk": "⚠️ Em risco",
        "delayed": "❌ Atrasado",
        "completed": "✨ Concluído",
        "in_progress": "🔄 Em andamento",
        "not_started": "⏳ Não iniciado",
        "pending": "⏳ Pendente",
        "cancelled": "⛔ Cancelado",
    }
    return status_map.get(value, value)


def format_esg_metric(value: Union[int, float], unit: Optional[str] = None) -> str:
    """Formata valor de métrica ESG."""
    if isinstance(value, float):
        formatted = f"{value:,.2f}"
    else:
        formatted = f"{value:,d}"

    if unit:
        formatted = f"{formatted} {unit}"

    return formatted


def format_version(version: str) -> str:
    """Formata número de versão."""
    if not version.startswith("v"):
        version = f"v{version}"
    return version


def format_trend(value: float, previous: float) -> str:
    """Formata tendência com seta."""
    if value > previous:
        return "↗️ Aumento"
    elif value < previous:
        return "↘️ Redução"
    return "➡️ Estável"


def format_progress(
    value: int, width: int = 50, fill: str = "=", empty: str = " "
) -> str:
    """Gera barra de progresso ASCII."""
    filled = int(width * value / 100)
    bar = fill * filled
    if value < 100:
        bar += ">"
    bar += empty * (width - len(bar))
    return f"[{bar}] {value}%"


# Registro de filtros
FILTERS = {
    "format_date": format_date,
    "format_esg_metric": format_esg_metric,
    "format_status": format_status,
    "format_version": format_version,
    "format_trend": format_trend,
    "format_progress": format_progress,
    "format_metric": format_metric,
    "to_percentage": to_percentage,
}

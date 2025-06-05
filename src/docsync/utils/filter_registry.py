"""
Registro central de filtros para templates.
"""

import logging
from datetime import datetime
from typing import Dict, Callable, Any, Optional

from jinja2 import Environment

from ..exceptions import FilterError

logger = logging.getLogger(__name__)

class FilterRegistry:
    """Gerenciador de filtros para templates."""
    
    def __init__(self):
        """Inicializa registro de filtros."""
        self._filters: Dict[str, Callable] = {}
        self._register_default_filters()
        
    def _register_default_filters(self) -> None:
        """Registra filtros padrão."""
        # Formatação de datas
        self.register("format_date", self.format_date)
        self.register("format_version", self.format_version)
        self.register("format_metric", self.format_metric)
        self.register("format_status", self.format_status)
        self.register("format_progress", self.format_progress)
        self.register("format_trend", self.format_trend)
        self.register("format_priority", self.format_priority)
        
    def register(self, name: str, filter_func: Callable) -> None:
        """
        Registra um novo filtro.
        
        Args:
            name: Nome do filtro
            filter_func: Função de filtro
        """
        if name in self._filters:
            logger.warning(f"Sobrescrevendo filtro existente: {name}")
            
        self._filters[name] = filter_func
        logger.debug(f"Filtro registrado: {name}")
        
    def setup_environment(self, env: Environment) -> None:
        """
        Configura ambiente Jinja2 com todos os filtros.
        
        Args:
            env: Ambiente Jinja2
        """
        try:
            for name, filter_func in self._filters.items():
                env.filters[name] = filter_func
        except Exception as e:
            logger.error(f"Erro ao configurar filtros: {e}")
            raise FilterError(f"Falha no registro de filtros: {e}")
            
    def get_filter(self, name: str) -> Optional[Callable]:
        """
        Obtém função de filtro por nome.
        
        Args:
            name: Nome do filtro
            
        Returns:
            Função de filtro ou None se não encontrada
        """
        return self._filters.get(name)
    
    # Implementação dos filtros padrão
    @staticmethod
    def format_date(value: Any, format: str = "%d/%m/%Y") -> str:
        """Formata data."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return value
        return value.strftime(format)
    
    @staticmethod
    def format_version(value: str) -> str:
        """Formata número de versão."""
        if not str(value).startswith("v"):
            return f"v{value}"
        return value
    
    @staticmethod
    def format_metric(
        value: Any,
        metric_type: str,
        unit: Optional[str] = None
    ) -> str:
        """Formata valor de métrica."""
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
    
    @staticmethod
    def format_status(status: str) -> str:
        """Formata status com emoji."""
        status_map = {
            "completed": "✅ Concluído",
            "in_progress": "🔄 Em Andamento",
            "pending": "⏳ Pendente",
            "delayed": "⚠️ Atrasado",
            "on_track": "✅ No Prazo",
            "at_risk": "⚠️ Em Risco",
            "blocked": "❌ Bloqueado"
        }
        return status_map.get(status.lower(), status)
    
    @staticmethod
    def format_progress(value: float, width: int = 20) -> str:
        """Formata barra de progresso ASCII."""
        fill = "="
        empty = "-"
        progress = int(width * value / 100)
        bar = fill * progress
        if progress < width:
            bar += ">"
        bar += empty * (width - len(bar))
        return f"[{bar}] {value:.1f}%"
    
    @staticmethod
    def format_trend(value: float, previous: float) -> str:
        """Formata tendência com seta."""
        if value > previous:
            return "↗️ Aumento"
        elif value < previous:
            return "↘️ Redução"
        return "➡️ Estável"
        
    @staticmethod
    def format_priority(priority: str) -> str:
        """Formata prioridade com cores."""
        priority_map = {
            "high": "🔴 Alta",
            "medium": "🟡 Média",
            "low": "🟢 Baixa"
        }
        return priority_map.get(priority.lower(), priority)
        
# Instância global do registro
filter_registry = FilterRegistry()


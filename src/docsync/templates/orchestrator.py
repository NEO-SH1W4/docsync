"""
Template orchestrator para relatórios ESG.

Este módulo fornece a infraestrutura para:
- Combinação inteligente de templates
- Gerenciamento de metadados
- Formatação consistente
- Validação de dados
- Geração multi-formato
"""

import logging
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.progress import Progress

from ..exceptions import OrchestratorError
from ..utils.filters import FILTERS

# Console para feedback visual
console = Console()
logger = logging.getLogger(__name__)


@dataclass
class TemplateConfig:
    """Configuração para renderização de template."""

    name: str
    sections: List[str]
    format: str
    metadata: Dict[str, Any]
    data: Dict[str, Any]
    output_path: Path


class TemplateOrchestrator:
    """
    Orquestrador de templates para relatórios ESG.

    Responsável por:
    - Carregamento de templates
    - Combinação de seções
    - Aplicação de formatação
    - Validação de dados
    - Geração de saída
    """

    def __init__(
        self,
        template_dir: Union[str, Path],
        config_path: Optional[Union[str, Path]] = None,
    ):
        """
        Inicializa o orquestrador.

        Args:
            template_dir: Diretório base dos templates
            config_path: Caminho para arquivo de configuração opcional
        """
        self.template_dir = Path(template_dir)
        self.config_path = Path(config_path) if config_path else None

        # Configura ambiente Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Registra filtros customizados
        for name, filter_func in FILTERS.items():
            self.env.filters[name] = filter_func

        # Carrega configuração se disponível
        self.config = self._load_config()

        logger.info(f"Orquestrador inicializado com diretório: {template_dir}")

    def _load_config(self) -> Dict:
        """Carrega configuração do orquestrador."""
        if not self.config_path or not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar configuração: {e}")
            return {}

    def _validate_template_config(self, config: TemplateConfig) -> None:
        """
        Valida configuração do template.

        Args:
            config: Configuração a ser validada

        Raises:
            OrchestratorError: Se a configuração for inválida
        """
        errors = []

        if not config.name:
            errors.append("Nome do template não especificado")

        if not config.sections:
            errors.append("Nenhuma seção especificada")

        if config.format not in ["md", "html"]:
            errors.append(f"Formato inválido: {config.format}")

        if not config.data:
            errors.append("Dados não fornecidos")

        if errors:
            raise OrchestratorError("\n".join(errors))

    def list_templates(self) -> Dict[str, List[str]]:
        """Lista templates disponíveis."""
        templates = {"sections": [], "layouts": []}

        try:
            # Lista seções disponíveis
            sections_path = self.template_dir / "guardrive/sections"
            if sections_path.exists():
                templates["sections"] = [
                    p.stem.split(".")[0] for p in sections_path.glob("*.md.jinja")
                ]

            # Lista layouts disponíveis
            layouts_path = self.template_dir / "guardrive/layouts"
            if layouts_path.exists():
                templates["layouts"] = [
                    p.stem.split(".")[0] for p in layouts_path.glob("*.md.jinja")
                ]
        except Exception as e:
            logger.error(f"Erro ao listar templates: {e}")
            raise

        return templates

    def generate_report(self, config: TemplateConfig) -> Path:
        """Gera relatório combinando seções de template."""
        try:
            # Valida configuração
            self._validate_template_config(config)

            with Progress() as progress:
                task = progress.add_task(
                    "Gerando relatório...", total=len(config.sections)
                )

                content_parts = []
                for section in config.sections:
                    template_path = (
                        f"guardrive/sections/{section}.{config.format}.jinja"
                    )
                    template = self.env.get_template(template_path)

                    # Renderiza seção
                    content = template.render(**config.data, metadata=config.metadata)
                    content_parts.append(content)

                    progress.update(task, advance=1)

                # Combina conteúdo
                final_content = "\n\n".join(content_parts)

                # Garante que diretório de saída existe
                config.output_path.parent.mkdir(parents=True, exist_ok=True)

                # Salva arquivo
                config.output_path.write_text(final_content, encoding="utf-8")
                logger.info(f"Relatório gerado: {config.output_path}")

                return config.output_path

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise

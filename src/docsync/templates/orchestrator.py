"""
Orquestrador de templates para geração de relatórios.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.progress import Progress

from .filters import FILTERS

logger = logging.getLogger(__name__)


@dataclass
class TemplateConfig:
    """Configuração para geração de relatório."""

    name: str
    sections: List[str]
    format: str
    metadata: Dict[str, Any]
    data: Dict[str, Any]
    output_path: Path


class TemplateOrchestrator:
    """Orquestrador de templates."""

    def __init__(self, template_dir: Path):
        """Inicializa o orquestrador com diretório base de templates."""
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Registra filtros personalizados
        for name, filter_func in FILTERS.items():
            self.env.filters[name] = filter_func

        logger.info(f"Orquestrador inicializado com diretório: {template_dir}")

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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.progress import Progress

from ..exceptions import OrchestratorError, TemplateError
from ..utils.filters import register_filters
from ..utils.validators import validate_esg_data

# Console para feedback visual
console = Console()


@dataclass
class TemplateConfig:
    """Configuração para renderização de template."""

    name: str
    sections: List[str]
    format: str
    metadata: Dict
    data: Dict
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
        self.logger = logging.getLogger(__name__)

        # Configura ambiente Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Registra filtros customizados
        register_filters(self.env)

        # Carrega configuração se disponível
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Carrega configuração do orquestrador."""
        if not self.config_path or not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar configuração: {e}")
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

    def _load_section_template(self, section: str, format: str) -> str:
        """
        Carrega template de uma seção.

        Args:
            section: Nome da seção
            format: Formato desejado (md/html)

        Returns:
            Conteúdo do template

        Raises:
            TemplateError: Se o template não for encontrado
        """
        try:
            template_path = f"guardrive/sections/{section}.{format}.jinja"
            return self.env.get_template(template_path)
        except Exception as e:
            raise TemplateError(f"Erro ao carregar template {section}: {e}")

    def _combine_sections(
        self, config: TemplateConfig, progress: Optional[Progress] = None
    ) -> str:
        """
        Combina múltiplas seções em um relatório.

        Args:
            config: Configuração do template
            progress: Objeto de progresso opcional

        Returns:
            Conteúdo combinado do relatório
        """
        sections = []
        task_id = None

        if progress:
            task_id = progress.add_task(
                "Combinando seções...", total=len(config.sections)
            )

        try:
            for section in config.sections:
                template = self._load_section_template(section, config.format)
                content = template.render(**config.data)
                sections.append(content)

                if progress and task_id:
                    progress.update(task_id, advance=1)

            return "\n\n".join(sections)

        except Exception as e:
            raise OrchestratorError(f"Erro ao combinar seções: {e}")

    def _apply_metadata(self, content: str, metadata: Dict) -> str:
        """
        Aplica metadados ao relatório.

        Args:
            content: Conteúdo do relatório
            metadata: Metadados a serem aplicados

        Returns:
            Conteúdo com metadados
        """
        try:
            template = self.env.from_string(content)
            return template.render(metadata=metadata)
        except Exception as e:
            raise OrchestratorError(f"Erro ao aplicar metadados: {e}")

    def generate_report(self, config: TemplateConfig, validate: bool = True) -> Path:
        """
        Gera relatório ESG completo.

        Args:
            config: Configuração do template
            validate: Se True, valida os dados antes de gerar

        Returns:
            Caminho do arquivo gerado

        Raises:
            OrchestratorError: Se houver erro na geração
        """
        try:
            # Valida configuração
            self._validate_template_config(config)

            # Valida dados ESG se solicitado
            if validate:
                validate_esg_data(config.data)

            with Progress() as progress:
                # Combina seções
                content = self._combine_sections(config, progress)

                # Aplica metadados
                if config.metadata:
                    content = self._apply_metadata(content, config.metadata)

                # Garante que diretório existe
                config.output_path.parent.mkdir(parents=True, exist_ok=True)

                # Escreve arquivo
                with open(config.output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                return config.output_path

        except Exception as e:
            raise OrchestratorError(f"Erro ao gerar relatório: {e}")

    def list_templates(self) -> Dict[str, List[str]]:
        """
        Lista templates disponíveis.

        Returns:
            Dicionário com templates por categoria
        """
        templates = {"sections": [], "layouts": []}

        try:
            sections_dir = self.template_dir / "guardrive" / "sections"
            if sections_dir.exists():
                for path in sections_dir.glob("*.jinja"):
                    name = path.stem.rsplit(".", 1)[0]
                    if name not in templates["sections"]:
                        templates["sections"].append(name)

            layouts_dir = self.template_dir / "guardrive" / "layouts"
            if layouts_dir.exists():
                for path in layouts_dir.glob("*.jinja"):
                    templates["layouts"].append(path.stem)

        except Exception as e:
            self.logger.error(f"Erro ao listar templates: {e}")

        return templates

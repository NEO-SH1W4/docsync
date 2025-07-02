"""Template rendering functionality."""

import logging
from pathlib import Path
from typing import Any, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from docsync.utils.filters import (
    format_date,
    format_metric,
    format_status,
    to_percentage,
)

logger = logging.getLogger(__name__)


class TemplateError(Exception):
    """Exception raised for template rendering errors."""


class TemplateRenderer:
    """Handles template rendering with custom filters."""

    def __init__(
        self,
        templates_dir: Optional[Union[str, Path]] = None,
        encoding: str = "utf-8",
    ) -> None:
        """Initialize template renderer.

        Args:
            templates_dir: Optional custom templates directory
            encoding: Template file encoding (default: utf-8)
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path(__file__).parent

        if not self.templates_dir.exists():
            msg = f"Templates directory not found: {self.templates_dir}"
            raise TemplateError(msg)

        logger.debug("Initializing template renderer at: %s", self.templates_dir)

        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir), encoding=encoding),
                autoescape=select_autoescape(["html", "xml"]),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Register custom filters
            self.env.filters["format_metric"] = format_metric
            self.env.filters["to_percentage"] = to_percentage
            self.env.filters["format_date"] = format_date
            self.env.filters["format_status"] = format_status

            logger.info("Template renderer initialized successfully")

        except Exception as e:
            logger.exception("Failed to initialize template renderer: %s", e)
            msg = f"Failed to initialize template renderer: {e}"
            raise TemplateError(msg)

    def list_templates(self) -> list[str]:
        """List all available templates."""
        try:
            return self.env.list_templates()
        except Exception as e:
            logger.exception("Failed to list templates: %s", e)
            msg = f"Failed to list templates: {e}"
            raise TemplateError(msg)

    def render(
        self,
        template_name: str,
        data: dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Render a template with provided data.

        Args:
            template_name: Name of template file
            data: Data to render in template
            output_path: Optional path to save rendered output

        Returns:
            Rendered template string

        Raises:
            TemplateError: If rendering fails
        """
        logger.debug("Rendering template: %s", template_name)

        try:
            # Load template
            template = self.env.get_template(template_name)

            # Render template
            rendered = template.render(**data)

            # Save output if path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                logger.debug("Writing rendered template to: %s", output_path)
                output_path.write_text(rendered, encoding="utf-8")
                logger.info("Template saved to: %s", output_path)

            return rendered

        except Exception as e:
            logger.exception("Failed to render template %s: %s", template_name, e)
            msg = f"Failed to render template '{template_name}': {e}"
            raise TemplateError(msg)

    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and is loadable.

        Args:
            template_name: Name of template to validate

        Returns:
            True if template is valid

        Raises:
            TemplateError: If template is invalid
        """
        try:
            self.env.get_template(template_name)
            return True
        except Exception as e:
            logger.exception("Invalid template %s: %s", template_name, e)
            msg = f"Invalid template '{template_name}': {e}"
            raise TemplateError(msg)

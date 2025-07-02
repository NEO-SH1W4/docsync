"""DocSync - Documentation synchronization and ESG report generation.

This package provides tools for:
- ESG report generation using templates
- Document synchronization across projects
- File watching and automatic updates
- Notion integration for documentation workflows
"""

__version__ = "0.1.0"
__author__ = "GUARDRIVE Team"
__email__ = "team@guardrive.io"

from .core import (
    DocSync,
    DocSyncError,
    DocumentSynchronizer,
    ReportGenerationError,
    TemplateError,
    generate_esg_report,
)

__all__ = [
    "DocSync",
    "DocSyncError",
    "DocumentSynchronizer",
    "ReportGenerationError",
    "TemplateError",
    "generate_esg_report",
]

"""
DocSync - Sistema de sincronização e gerenciamento de documentação.
"""

__version__ = "0.1.0"
__author__ = "GUARDRIVE Team"
__email__ = "team@guardrive.io"

from .core import DocSync

__all__ = ["DocSync"]

"""
DocSync - Documentation synchronization and ESG report generation.

This package provides tools for:
- ESG report generation using templates
- Document synchronization across projects
- File watching and automatic updates
"""

__version__ = "0.1.0"

from docsync.core import (
    DocSyncError,
    DocumentSynchronizer,
    ReportGenerationError,
    TemplateError,
    generate_esg_report,
)

__all__ = [
    "DocumentSynchronizer",
    "DocSyncError",
    "ReportGenerationError",
    "TemplateError",
    "generate_esg_report",
]

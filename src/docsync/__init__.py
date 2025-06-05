"""
DocSync - Sistema de sincronização e gerenciamento de documentação.
"""

__version__ = "0.1.0"
__author__ = "GUARDRIVE Team"
__email__ = "team@guardrive.io"

from .core import (
    DocSync,
    DocumentSynchronizer,
    DocSyncError,
    ReportGenerationError,
    TemplateError,
    generate_esg_report,
)

__all__ = [
    "DocSync",
    "DocumentSynchronizer",
    "DocSyncError",
    "ReportGenerationError",
    "TemplateError",
    "generate_esg_report",
]


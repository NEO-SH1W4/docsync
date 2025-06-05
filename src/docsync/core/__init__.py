"""
Core functionality for DocSync system.
"""

from .base import (
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

"""
Módulo principal do DocSync.
"""

from .sync import DocSync

__all__ = ["DocSync"]


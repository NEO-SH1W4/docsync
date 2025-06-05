"""Public interface for the :mod:`docsync.core` package."""

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


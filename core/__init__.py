"""DocSync core module initialization.
Exports main classes for file monitoring, synchronization, validation and backup.
"""

from .backup import BackupManager, BackupMetadata
from .monitor import DocSyncEventHandler, FileMonitor
from .sync import FileSync
from .validate import FileValidator, ValidationResult

__all__ = [
    "BackupManager",
    "BackupMetadata",
    "DocSyncEventHandler",
    "FileMonitor",
    "FileSync",
    "FileValidator",
    "ValidationResult",
]

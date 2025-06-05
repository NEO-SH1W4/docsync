"""
DocSync core module initialization.
Exports main classes for file monitoring, synchronization, validation and backup.
"""

from .monitor import FileMonitor, DocSyncEventHandler
from .sync import FileSync
from .validate import FileValidator, ValidationResult
from .backup import BackupManager, BackupMetadata

__all__ = [
    'FileMonitor',
    'DocSyncEventHandler',
    'FileSync',
    'FileValidator',
    'ValidationResult',
    'BackupManager',
    'BackupMetadata'
]


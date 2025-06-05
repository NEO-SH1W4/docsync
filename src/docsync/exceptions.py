"""
Exceções customizadas para o DocSync.
"""

class DocSyncError(Exception):
    """Erro base para todas as exceções do DocSync."""
    pass

class TemplateError(DocSyncError):
    """Erro relacionado a templates."""
    pass

class OrchestratorError(DocSyncError):
    """Erro no orquestrador de templates."""
    pass

class ValidationError(DocSyncError):
    """Erro de validação de dados."""
    pass

class ConfigError(DocSyncError):
    """Erro de configuração."""
    pass

class SyncError(DocSyncError):
    """Erro de sincronização."""
    pass

class FilterError(DocSyncError):
    """Erro relacionado ao processamento de filtros."""
    pass


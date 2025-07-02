"""Exceções customizadas para o DocSync."""


class DocSyncError(Exception):
    """Erro base para todas as exceções do DocSync."""


class TemplateError(DocSyncError):
    """Erro relacionado a templates."""


class OrchestratorError(DocSyncError):
    """Erro no orquestrador de templates."""


class ValidationError(DocSyncError):
    """Erro de validação de dados."""


class ConfigError(DocSyncError):
    """Erro de configuração."""


class SyncError(DocSyncError):
    """Erro de sincronização."""


class FilterError(DocSyncError):
    """Erro relacionado ao processamento de filtros."""

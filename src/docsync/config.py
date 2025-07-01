"""
Módulo de configuração do DocSync.

Fornece funcionalidades para carregar, validar e gerenciar configurações
do sistema de documentação, incluindo suporte para:
- Carregamento de arquivos YAML
- Substituição por variáveis de ambiente
- Validação de configuração
- Valores padrão
- Logging configurável

Author: DocSync Team
Date: 2025-06-03
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from yaml.parser import ParserError

# Configuração do logging
logger = logging.getLogger(__name__)


@dataclass
class ESGConfig:
    """Configuração para geração de relatórios ESG."""

    metrics_enabled: bool = True
    custom_templates: Dict[str, str] = field(default_factory=dict)
    output_format: str = "markdown"
    validation_level: str = "strict"


class DocumentType(Enum):
    """Tipos de documentos suportados."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    PRODUCT = "product"
    ASSET = "asset"
    META = "meta"


@dataclass
class VersionControlConfig:
    """Configuração para controle de versão de documentos."""

    enabled: bool = True
    provider: str = "git"
    backup_enabled: bool = True
    backup_interval: int = 3600  # em segundos
    retention_days: int = 30
    commit_message_template: str = "doc: {action} - {path}"


@dataclass
class PathMappingConfig:
    """Configuração para mapeamento de caminhos entre GUARDRIVE_DOCS e AREA_DEV."""

    source_path: str = field(default="")
    target_path: str = field(default="")
    doc_type: DocumentType = field(default=DocumentType.TECHNICAL)
    bidirectional: bool = True
    ignore_patterns: List[str] = field(
        default_factory=lambda: [".git", "__pycache__", "*.pyc"]
    )


@dataclass
class DocumentHandlerConfig:
    """Configuração para manipulação de diferentes tipos de documentos."""

    file_extensions: List[str] = field(
        default_factory=lambda: ["md", "rst", "txt", "pdf"]
    )
    preserve_metadata: bool = True
    convert_formats: bool = False
    validate_links: bool = True
    check_references: bool = True


@dataclass
class GuardriveConfig:
    """Configuração específica para integração com GUARDRIVE."""

    enabled: bool = True
    base_path: str = field(default="")
    docs_path: str = field(default="GUARDRIVE_DOCS")
    dev_path: str = field(default="AREA_DEV")
    path_mappings: List[PathMappingConfig] = field(default_factory=list)
    doc_handlers: Dict[str, DocumentHandlerConfig] = field(default_factory=dict)
    version_control: VersionControlConfig = field(default_factory=VersionControlConfig)
    conflict_resolution: str = "manual"
    sync_schedule: str = "*/15 * * * *"  # Formato cron
    validation_level: str = "strict"


@dataclass
class SyncConfig:
    """Configuração para sincronização de documentação."""

    watch_paths: List[str] = field(default_factory=list)
    ignore_patterns: List[str] = field(default_factory=list)
    auto_sync: bool = True
    sync_interval: int = 300
    real_time_sync: bool = False
    conflict_handling: str = "ask"
    retry_attempts: int = 3
    retry_delay: int = 60
    checksum_verification: bool = True
    preserve_timestamps: bool = True
    sync_metadata: bool = True
    sync_permissions: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB em bytes


@dataclass
class Config:
    """Configuração principal do DocSync."""

    esg: ESGConfig = field(default_factory=ESGConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    guardrive: GuardriveConfig = field(default_factory=GuardriveConfig)
    templates_dir: str = "templates"
    output_dir: str = "output"
    log_level: str = "INFO"
    backup_dir: str = "backups"
    temp_dir: str = "temp"


# Configurações padrão
DEFAULT_CONFIG = {
    "esg": {
        "metrics_enabled": True,
        "custom_templates": {},
        "output_format": "markdown",
        "validation_level": "strict",
    },
    "sync": {
        "watch_paths": [],
        "ignore_patterns": [".git", "__pycache__", "*.pyc"],
        "auto_sync": True,
        "sync_interval": 300,
        "real_time_sync": False,
        "conflict_handling": "ask",
        "retry_attempts": 3,
        "retry_delay": 60,
        "checksum_verification": True,
        "preserve_timestamps": True,
        "sync_metadata": True,
        "sync_permissions": True,
        "max_file_size": 104857600,
    },
    "guardrive": {
        "enabled": True,
        "base_path": "",
        "docs_path": "GUARDRIVE_DOCS",
        "dev_path": "AREA_DEV",
        "path_mappings": [],
        "doc_handlers": {
            "default": {
                "file_extensions": ["md", "rst", "txt", "pdf"],
                "preserve_metadata": True,
                "convert_formats": False,
                "validate_links": True,
                "check_references": True,
            }
        },
        "version_control": {
            "enabled": True,
            "provider": "git",
            "backup_enabled": True,
            "backup_interval": 3600,
            "retention_days": 30,
            "commit_message_template": "doc: {action} - {path}",
        },
        "conflict_resolution": "manual",
        "sync_schedule": "*/15 * * * *",
        "validation_level": "strict",
    },
    "templates_dir": "templates",
    "output_dir": "output",
    "backup_dir": "backups",
    "temp_dir": "temp",
    "log_level": "INFO",
}


def load_config(config_path: Union[str, Path, None] = None) -> Dict[str, Any]:
    """
    Carrega a configuração do DocSync de um arquivo YAML e aplica
    variáveis de ambiente e valores padrão.

    Args:
        config_path: Caminho para o arquivo de configuração YAML.
                   Se None, usa apenas valores padrão e variáveis de ambiente.

    Returns:
        Dict[str, Any]: Configuração consolidada

    Raises:
        FileNotFoundError: Se o arquivo de configuração não existir
        yaml.YAMLError: Se houver erro no parse do YAML
        ValueError: Se a configuração for inválida
    """
    config = DEFAULT_CONFIG.copy()

    # Carrega arquivo de configuração se especificado
    if config_path:
        config_path = Path(config_path)
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        _deep_update(config, file_config)
                logger.info(f"Configuração carregada de {config_path}")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
        except ParserError as e:
            logger.error(f"Erro ao parsear YAML: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            raise

    # Aplica variáveis de ambiente
    _apply_env_vars(config)

    # Valida a configuração
    _validate_config(config)

    return config


def _deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Atualiza um dicionário recursivamente."""
    for key, value in update_dict.items():
        if (
            key in base_dict
            and isinstance(base_dict[key], dict)
            and isinstance(value, dict)
        ):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


def _apply_env_vars(config: Dict[str, Any]) -> None:
    """Aplica variáveis de ambiente à configuração."""
    env_mappings = {
        "DOCSYNC_TEMPLATES_DIR": ("templates_dir", str),
        "DOCSYNC_OUTPUT_DIR": ("output_dir", str),
        "DOCSYNC_LOG_LEVEL": ("log_level", str),
        "DOCSYNC_ESG_METRICS_ENABLED": ("esg.metrics_enabled", bool),
        "DOCSYNC_SYNC_INTERVAL": ("sync.sync_interval", int),
        "DOCSYNC_AUTO_SYNC": ("sync.auto_sync", bool),
    }

    for env_var, (config_path, type_conv) in env_mappings.items():
        if env_var in os.environ:
            try:
                value = os.environ[env_var]
                if type_conv == bool:
                    value = value.lower() in ("true", "1", "yes")
                elif type_conv == int:
                    value = int(value)

                # Atualiza configuração
                parts = config_path.split(".")
                current = config
                for part in parts[:-1]:
                    current = current[part]
                current[parts[-1]] = value

                logger.debug(f"Aplicada variável de ambiente {env_var}")
            except (ValueError, KeyError) as e:
                logger.warning(f"Erro ao processar variável de ambiente {env_var}: {e}")


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Valida a configuração carregada.

    Raises:
        ValueError: Se a configuração for inválida
    """
    required_fields = {
        "templates_dir": str,
        "output_dir": str,
        "backup_dir": str,
        "temp_dir": str,
        "log_level": str,
        "esg": dict,
        "sync": dict,
        "guardrive": dict,
    }

    for field, expected_type in required_fields.items():
        if field not in config:
            raise ValueError(f"Campo obrigatório ausente: {field}")
        if not isinstance(config[field], expected_type):
            raise ValueError(
                f"Tipo inválido para {field}: esperado {expected_type}, recebido {type(config[field])}"
            )

    # Valida níveis específicos
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if config["log_level"].upper() not in valid_log_levels:
        raise ValueError(f"Nível de log inválido: {config['log_level']}")

    # Valida diretórios
    templates_dir = Path(config["templates_dir"])
    if not templates_dir.exists() and not templates_dir.is_absolute():
        logger.warning(f"Diretório de templates não encontrado: {templates_dir}")

    # Valida configuração ESG
    if not isinstance(config["esg"].get("metrics_enabled"), bool):
        raise ValueError("esg.metrics_enabled deve ser booleano")

    # Valida configuração de sincronização
    if not isinstance(config["sync"].get("sync_interval"), int):
        raise ValueError("sync.sync_interval deve ser inteiro")

    # Valida configuração do GUARDRIVE
    guardrive_config = config.get("guardrive", {})
    if guardrive_config.get("enabled"):
        if not guardrive_config.get("base_path"):
            raise ValueError(
                "guardrive.base_path é obrigatório quando guardrive está habilitado"
            )

        # Valida caminhos do GUARDRIVE
        docs_path = Path(guardrive_config["base_path"]) / guardrive_config["docs_path"]
        dev_path = Path(guardrive_config["base_path"]) / guardrive_config["dev_path"]

        if not docs_path.exists():
            logger.warning(f"Diretório GUARDRIVE_DOCS não encontrado: {docs_path}")
        if not dev_path.exists():
            logger.warning(f"Diretório AREA_DEV não encontrado: {dev_path}")

        # Valida mapeamentos de caminhos
        for mapping in guardrive_config.get("path_mappings", []):
            if not mapping.get("source_path") or not mapping.get("target_path"):
                raise ValueError(
                    "Mapeamentos de caminho devem ter source_path e target_path"
                )

        # Valida configuração de controle de versão
        vc_config = guardrive_config.get("version_control", {})
        if vc_config.get("enabled") and not vc_config.get("provider"):
            raise ValueError(
                "Provider de controle de versão é obrigatório quando habilitado"
            )

    logger.info("Configuração validada com sucesso")

"""
Utilitários para gerenciamento de configuração.
"""

import logging
from pathlib import Path
from typing import Dict, Union

import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: Union[str, Path]) -> Dict:
    """
    Carrega configuração de arquivo YAML.

    Args:
        config_path: Caminho do arquivo de configuração

    Returns:
        Dict: Configuração carregada

    Raises:
        FileNotFoundError: Se o arquivo não existir
        yaml.YAMLError: Se houver erro no formato do arquivo
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_path}"
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.debug("Configuração carregada: %s", config_path)
            return config
    except yaml.YAMLError as e:
        logger.error("Erro ao carregar configuração: %s", e)
        raise

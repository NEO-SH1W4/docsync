"""
Utilitários para validação, manipulação de arquivos e processamento de templates.
"""

import json
import logging
import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# Configuração de logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado da validação de estrutura."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class StructureError(Exception):
    """Exceção para erros de estrutura."""


class PermissionError(Exception):
    """Exceção para erros de permissão."""


def validate_structure(
    root_path: Path,
    required_dirs: List[str],
    required_files: Optional[List[str]] = None,
    template_dirs: Optional[List[str]] = None,
) -> ValidationResult:
    """
    Valida a estrutura de diretórios e arquivos.

    Args:
        root_path: Caminho raiz da estrutura
        required_dirs: Lista de diretórios obrigatórios
        required_files: Lista opcional de arquivos obrigatórios
        template_dirs: Lista opcional de diretórios de templates

    Returns:
        ValidationResult com status e mensagens
    """
    errors = []
    warnings = []

    try:
        # Verificar existência do diretório raiz
        if not root_path.exists():
            errors.append(f"Diretório raiz não encontrado: {root_path}")
            return ValidationResult(False, errors, warnings)

        # Verificar permissões do diretório raiz
        if not os.access(root_path, os.R_OK | os.W_OK):
            errors.append(f"Permissões insuficientes no diretório raiz: {root_path}")
            return ValidationResult(False, errors, warnings)

        # Verificar diretórios obrigatórios
        for dir_name in required_dirs:
            dir_path = root_path / dir_name
            if not dir_path.exists():
                errors.append(f"Diretório obrigatório não encontrado: {dir_name}")
                continue

            if not dir_path.is_dir():
                errors.append(f"Caminho não é um diretório: {dir_name}")
                continue

            if not os.access(dir_path, os.R_OK | os.W_OK):
                errors.append(f"Permissões insuficientes no diretório: {dir_name}")

        # Verificar arquivos obrigatórios
        if required_files:
            for file_name in required_files:
                file_path = root_path / file_name
                if not file_path.exists():
                    errors.append(f"Arquivo obrigatório não encontrado: {file_name}")
                    continue

                if not file_path.is_file():
                    errors.append(f"Caminho não é um arquivo: {file_name}")
                    continue

                if not os.access(file_path, os.R_OK):
                    errors.append(f"Permissões insuficientes no arquivo: {file_name}")

        # Verificar diretórios de templates
        if template_dirs:
            for template_dir in template_dirs:
                dir_path = root_path / template_dir
                if not dir_path.exists():
                    errors.append(
                        f"Diretório de templates não encontrado: {template_dir}"
                    )
                    continue

                # Verificar se há templates no diretório
                template_files = list(dir_path.glob("*.j2"))
                if not template_files:
                    warnings.append(f"Nenhum template encontrado em: {template_dir}")

                # Verificar permissões dos templates
                for template in template_files:
                    if not os.access(template, os.R_OK):
                        errors.append(
                            f"Permissões insuficientes no template: {template}"
                        )

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    except Exception as e:
        errors.append(f"Erro ao validar estrutura: {str(e)}")
        logger.exception("Falha na validação de estrutura")
        return ValidationResult(False, errors, warnings)


def ensure_directory(path: Path) -> None:
    """
    Garante que um diretório existe com as permissões corretas.

    Args:
        path: Caminho do diretório
    """
    try:
        path.mkdir(parents=True, exist_ok=True)

        # Definir permissões (rw- rw- r--)
        os.chmod(
            path,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH,
        )

    except Exception as e:
        logger.error(f"Erro ao criar diretório {path}: {e}")
        raise StructureError(f"Não foi possível criar diretório: {str(e)}")


def safe_remove(path: Path) -> None:
    """
    Remove arquivo ou diretório de forma segura.

    Args:
        path: Caminho a ser removido
    """
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except Exception as e:
        logger.error(f"Erro ao remover {path}: {e}")
        raise StructureError(f"Não foi possível remover: {str(e)}")


def normalize_path(path: str | Path) -> Path:
    """
    Normaliza um caminho, expandindo variáveis de ambiente e user home.

    Args:
        path: Caminho a ser normalizado

    Returns:
        Path normalizado
    """
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve()


def is_writable(path: Path) -> bool:
    """
    Verifica se um caminho tem permissão de escrita.

    Args:
        path: Caminho a ser verificado

    Returns:
        True se tiver permissão de escrita
    """
    try:
        if path.exists():
            return os.access(path, os.W_OK)
        return os.access(path.parent, os.W_OK)
    except Exception:
        return False


def find_files(
    root: Path, patterns: List[str], exclude_dirs: Optional[Set[str]] = None
) -> List[Path]:
    """
    Encontra arquivos que correspondem aos padrões dados.

    Args:
        root: Diretório raiz para busca
        patterns: Lista de padrões glob
        exclude_dirs: Conjunto de diretórios a serem ignorados

    Returns:
        Lista de caminhos encontrados
    """
    if exclude_dirs is None:
        exclude_dirs = set()

    found_files = []
    try:
        for pattern in patterns:
            for file_path in root.rglob(pattern):
                if not any(d in file_path.parents for d in exclude_dirs):
                    found_files.append(file_path)
    except Exception as e:
        logger.error(f"Erro ao buscar arquivos: {e}")

    return sorted(set(found_files))


def load_metadata(path: Path) -> Dict:
    """
    Carrega metadados de um arquivo YAML ou JSON.

    Args:
        path: Caminho do arquivo

    Returns:
        Dicionário com metadados
    """
    try:
        content = path.read_text(encoding="utf-8")
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(content) or {}
        elif path.suffix == ".json":
            return json.loads(content)
        else:
            raise ValueError(f"Formato não suportado: {path.suffix}")
    except Exception as e:
        logger.error(f"Erro ao carregar metadados de {path}: {e}")
        return {}


def save_metadata(path: Path, data: Dict) -> None:
    """
    Salva metadados em arquivo YAML ou JSON.

    Args:
        path: Caminho do arquivo
        data: Dados a serem salvos
    """
    try:
        content = None
        if path.suffix in [".yaml", ".yml"]:
            content = yaml.dump(data, allow_unicode=True)
        elif path.suffix == ".json":
            content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Formato não suportado: {path.suffix}")

        path.write_text(content, encoding="utf-8")
    except Exception as e:
        logger.error(f"Erro ao salvar metadados em {path}: {e}")
        raise


def create_backup(path: Path) -> Path:
    """
    Cria um backup do arquivo ou diretório.

    Args:
        path: Caminho a ser backupeado

    Returns:
        Caminho do arquivo de backup
    """
    backup_path = path.with_suffix(path.suffix + ".bak")
    try:
        if path.is_file():
            shutil.copy2(path, backup_path)
        elif path.is_dir():
            shutil.copytree(path, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup de {path}: {e}")
        raise


def restore_backup(backup_path: Path, original_path: Path) -> None:
    """
    Restaura um backup.

    Args:
        backup_path: Caminho do backup
        original_path: Caminho original
    """
    try:
        if original_path.exists():
            safe_remove(original_path)

        if backup_path.is_file():
            shutil.copy2(backup_path, original_path)
        elif backup_path.is_dir():
            shutil.copytree(backup_path, original_path)

        safe_remove(backup_path)
    except Exception as e:
        logger.error(f"Erro ao restaurar backup {backup_path}: {e}")
        raise

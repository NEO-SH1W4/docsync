"""
Configuração e fixtures compartilhadas para testes do DOCSYNC.
Fornece estrutura base para testes de integração e unitários.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import pytest
import yaml
from _pytest.fixtures import FixtureRequest

# Configurações Padrão
DEFAULT_CONFIG = {
    "processing": {"max_threads": 4, "cache_ttl": 3600, "batch_size": 100},
    "monitoring": {"enabled": True, "interval": 1.0, "max_queue_size": 1000},
    "validation": {
        "strict_mode": True,
        "max_errors": 10,
        "required_fields": ["title", "version"],
    },
}


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Configuração base para testes."""
    return DEFAULT_CONFIG.copy()


@pytest.fixture
def temp_base_dir() -> Generator[Path, None, None]:
    """Cria e gerencia diretório base temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_doc_dir(temp_base_dir: Path) -> Generator[Path, None, None]:
    """Cria estrutura de diretórios para documentos de teste."""
    doc_dir = temp_base_dir / "docs"
    doc_dir.mkdir(parents=True)

    # Criar subdiretórios padrão
    (doc_dir / "technical").mkdir()
    (doc_dir / "business").mkdir()
    (doc_dir / "meta").mkdir()

    yield doc_dir

    # Cleanup é automático via context manager do temp_base_dir


@pytest.fixture
def sample_doc_content() -> str:
    """Conteúdo markdown de exemplo para testes."""
    return """---
title: Test Document
version: 1.0.0
author: Test Author
date: 2025-06-03
---

# Test Document

## Section 1
Content for section 1.

## Section 2
Content for section 2.

```python
def test_function():
    return True
```
"""


@pytest.fixture
def sample_yaml_content() -> str:
    """Conteúdo YAML de exemplo para testes."""
    return """
config:
  enabled: true
  max_depth: 3
  patterns:
    - "*.md"
    - "*.yaml"
validation:
  rules:
    - check_structure
    - validate_links
"""


@pytest.fixture
def create_test_file(temp_doc_dir: Path):
    """Helper fixture para criar arquivos de teste."""

    def _create_file(name: str, content: str, subdir: Optional[str] = None) -> Path:
        if subdir:
            dir_path = temp_doc_dir / subdir
            dir_path.mkdir(exist_ok=True)
        else:
            dir_path = temp_doc_dir

        file_path = dir_path / name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_file


@pytest.fixture
def validate_document():
    """Helper fixture para validação de documentos."""

    def _validate(content: str, expected_structure: Dict[str, Any]) -> List[str]:
        errors = []

        # Validar metadados YAML
        try:
            doc_parts = content.split("---\n")
            if len(doc_parts) >= 3:
                metadata = yaml.safe_load(doc_parts[1])
                if not isinstance(metadata, dict):
                    errors.append("Metadados inválidos")
            else:
                errors.append("Documento não contém metadados YAML")
        except yaml.YAMLError:
            errors.append("Erro ao parsear metadados YAML")

        # Validar estrutura
        if "sections" in expected_structure:
            sections = [line for line in content.split("\n") if line.startswith("#")]
            if len(sections) != len(expected_structure["sections"]):
                errors.append(
                    f"Número incorreto de seções: "
                    f"esperado {len(expected_structure['sections'])}, "
                    f"encontrado {len(sections)}"
                )

        # Validar código
        if "code_blocks" in expected_structure:
            code_blocks = content.count("```")
            if code_blocks != expected_structure["code_blocks"] * 2:  # início e fim
                errors.append(
                    f"Número incorreto de blocos de código: "
                    f"esperado {expected_structure['code_blocks']}, "
                    f"encontrado {code_blocks//2}"
                )

        return errors

    return _validate


@pytest.fixture
def mock_file_monitor(monkeypatch):
    """Mock para o sistema de monitoramento de arquivos."""

    class MockMonitor:
        def __init__(self):
            self.events = []
            self.running = False

        def start(self):
            self.running = True

        def stop(self):
            self.running = False

        def add_event(self, event_type: str, path: str):
            if self.running:
                self.events.append(
                    {"type": event_type, "path": path, "processed": False}
                )

    monitor = MockMonitor()
    monkeypatch.setattr("src.monitoring.FileMonitor", lambda: monitor)
    return monitor


@pytest.fixture
def cleanup_test_files():
    """Fixture para limpeza de arquivos após testes."""
    temp_files = []

    def _register_file(file_path: str):
        temp_files.append(file_path)

    yield _register_file

    # Limpar arquivos após o teste
    for file_path in temp_files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Erro ao limpar arquivo {file_path}: {e}")


@pytest.fixture
def assert_doc_structure():
    """Helper para verificar estrutura de documentos."""

    def _assert_structure(content: str, expected: Dict[str, Any]) -> List[str]:
        issues = []

        # Verificar título
        if not content.startswith("# "):
            issues.append("Documento deve começar com título (h1)")

        # Verificar seções
        if "sections" in expected:
            sections = [
                line.strip()
                for line in content.split("\n")
                if line.strip().startswith("#")
            ]
            if sections != expected["sections"]:
                issues.append(
                    f"Estrutura de seções incorreta. "
                    f"Esperado: {expected['sections']}, "
                    f"Encontrado: {sections}"
                )

        # Verificar metadados
        if "metadata" in expected:
            try:
                doc_parts = content.split("---\n")
                if len(doc_parts) >= 3:
                    metadata = yaml.safe_load(doc_parts[1])
                    for key, value in expected["metadata"].items():
                        if key not in metadata:
                            issues.append(f"Metadado ausente: {key}")
                        elif metadata[key] != value:
                            issues.append(f"Valor incorreto para {key}")
                else:
                    issues.append("Metadados YAML ausentes")
            except Exception as e:
                issues.append(f"Erro ao validar metadados: {str(e)}")

        return issues

    return _assert_structure


"""
Shared test fixtures for DOCSYNC tests.
"""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Dict

import pytest


@pytest.fixture
def test_logger():
    """Create a test logger instance."""
    logger = logging.getLogger("docsync_test")
    logger.setLevel(logging.DEBUG)

    # Add console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@pytest.fixture
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix="docsync_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def setup_test_files(
    test_data_dir: Path,
) -> Callable[[Dict[str, str]], Dict[str, Path]]:
    """Create test files in the temporary directory."""

    def _create_files(file_contents: Dict[str, str]) -> Dict[str, Path]:
        created_files = {}
        for filename, content in file_contents.items():
            file_path = test_data_dir / filename
            file_path.write_text(content)
            created_files[filename] = file_path
        return created_files

    return _create_files


@pytest.fixture
def sample_templates(test_data_dir: Path) -> Dict[str, Path]:
    """Create sample document templates."""
    templates = {
        "technical.md": """---
title: {title}
version: {version}
status: draft
---
# Technical Documentation
## Overview
{overview}
""",
        "architecture.md": """---
title: System Architecture
version: 1.0
---
# Architecture Documentation
## Components
{components}
""",
        "config.yaml": """
version: {version}
project: {project}
settings:
  enabled: true
  sync_interval: 60
""",
    }

    template_files = {}
    for name, content in templates.items():
        path = test_data_dir / "templates" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        template_files[name] = path

    return template_files


@pytest.fixture(autouse=True)
def cleanup_after_test(test_data_dir: Path):
    """Cleanup any test artifacts after each test."""
    yield
    # Cleanup temporary files
    for item in test_data_dir.glob("**/*"):
        if item.is_file():
            item.unlink()


@pytest.fixture
def mock_file_system(test_data_dir: Path):
    """Create a mock file system structure."""
    structure = {
        "docs": {
            "technical": ["api.md", "architecture.md"],
            "business": ["requirements.md"],
            "product": ["roadmap.md"],
        },
        "config": ["docsync.yaml"],
        "templates": ["technical.md", "business.md"],
        "backup": {},
    }

    for category, subcategories in structure.items():
        if isinstance(subcategories, dict):
            for subcategory, files in subcategories.items():
                folder = test_data_dir / category / subcategory
                folder.mkdir(parents=True, exist_ok=True)
                for file in files:
                    (folder / file).touch()
        else:
            folder = test_data_dir / category
            folder.mkdir(parents=True, exist_ok=True)
            for file in subcategories:
                (folder / file).touch()

    return test_data_dir


@pytest.fixture
def mock_sync_target(test_data_dir: Path):
    """Create a mock synchronization target."""
    sync_dir = test_data_dir / "sync_target"
    sync_dir.mkdir(parents=True, exist_ok=True)
    return sync_dir


import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml


@pytest.fixture(scope="session")
def test_data_dir():
    """
    Cria diretório temporário para dados de teste que persiste durante toda a sessão
    """
    test_dir = tempfile.mkdtemp()
    yield test_dir
    shutil.rmtree(test_dir)


@pytest.fixture
def setup_test_files(test_data_dir):
    """
    Configura arquivos de teste padrão
    """

    def _create_files(files_dict: Dict[str, Any]):
        created_files = {}
        for fname, content in files_dict.items():
            fpath = Path(test_data_dir) / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(content, dict):
                fpath.write_text(yaml.dump(content))
            else:
                fpath.write_text(str(content))

            created_files[fname] = fpath
        return created_files

    return _create_files


@pytest.fixture
def mock_quantum_state():
    """
    Mock para estados quânticos durante testes
    """

    class MockQuantumState:
        def __init__(self):
            self.coherence = 1.0
            self.entanglement = {}

        def evolve(self):
            self.coherence *= 0.99

        def entangle(self, other):
            self.entanglement[id(other)] = 0.9

        def measure(self):
            return {
                "coherence": self.coherence,
                "entanglement_count": len(self.entanglement),
            }

    return MockQuantumState()


@pytest.fixture
def mock_consciousness():
    """
    Mock para consciência durante testes
    """

    class MockConsciousness:
        def __init__(self):
            self.awareness = 1.0
            self.connections = {}
            self.patterns = set()

        def process(self, data):
            self.patterns.add(hash(str(data)))
            return {"processed": True, "patterns_found": len(self.patterns)}

        def connect(self, other):
            self.connections[id(other)] = 0.95

        def get_state(self):
            return {
                "awareness": self.awareness,
                "connection_count": len(self.connections),
                "pattern_count": len(self.patterns),
            }

    return MockConsciousness()


@pytest.fixture
def test_logger():
    """
    Logger configurado para testes
    """
    import logging

    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    return logger


@pytest.fixture
def async_test_timeout():
    """
    Timeout padrão para testes assíncronos
    """
    return 5  # segundos

"""
Testes de integração para o sistema de processamento de documentação.
Valida o fluxo completo de processamento, cache e monitoramento.
"""

import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Generator

import pytest
import yaml

from src.ai_processor import AIEnhancedMonitor, DocumentProcessor


@pytest.fixture
def test_doc_content() -> str:
    """Retorna conteúdo de teste para documento markdown."""
    return """---
title: Test Document
version: 1.0.0
author: Test Author
date: 2025-06-03
---

# Introduction

This is a test document for integration testing.

## Installation

```python
pip install docsync
```

## Usage

Here's how to use the system:

```python
from docsync import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_file('doc.md')
```

## Examples

Check the examples directory for more.
"""


@pytest.fixture
def test_yaml_content() -> str:
    """Retorna conteúdo de teste para arquivo YAML."""
    return """
config:
  enabled: true
  max_depth: 3
  patterns:
    - "*.md"
    - "*.yaml"
processing:
  threads: 4
  cache_ttl: 3600
validation:
  rules:
    - check_structure
    - validate_links
"""


@pytest.fixture
def temp_doc_dir() -> Generator[Path, None, None]:
    """Cria diretório temporário com arquivos de teste."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = Path(temp_dir)

        # Criar arquivo markdown
        md_file = dir_path / "test.md"
        md_file.write_text(pytest.test_doc_content, encoding="utf-8")

        # Criar arquivo yaml
        yaml_file = dir_path / "config.yaml"
        yaml_file.write_text(pytest.test_yaml_content, encoding="utf-8")

        yield dir_path


def test_markdown_processing(temp_doc_dir: Path):
    """Testa processamento completo de arquivo markdown."""
    processor = DocumentProcessor()
    md_file = temp_doc_dir / "test.md"

    result = processor.process_file(md_file)

    # Verificar metadados
    assert result["metadata"] == {
        "title": "Test Document",
        "version": "1.0.0",
        "author": "Test Author",
        "date": "2025-06-03",
    }

    # Verificar estrutura
    assert len(result["headers"]) == 4
    assert [h["text"] for h in result["headers"]] == [
        "Introduction",
        "Installation",
        "Usage",
        "Examples",
    ]

    # Verificar blocos de código
    assert len(result["code_blocks"]) == 2
    assert all(block["language"] == "python" for block in result["code_blocks"])

    # Verificar qualidade
    quality = result["quality"]
    assert (
        quality["metrics"]["completeness"] == 1.0
    )  # Todas seções requeridas presentes
    assert quality["metrics"]["structure"] > 0.8  # Boa estrutura hierárquica
    assert quality["metrics"]["metadata_quality"] == 1.0  # Todos metadados presentes


def test_yaml_processing(temp_doc_dir: Path):
    """Testa processamento de arquivo YAML."""
    processor = DocumentProcessor()
    yaml_file = temp_doc_dir / "config.yaml"

    result = processor.process_file(yaml_file)

    # Verificar estrutura
    assert result["type"] == "yaml"
    assert "config" in result["content"]
    assert "processing" in result["content"]
    assert "validation" in result["content"]

    # Verificar análise estrutural
    structure = result["structure"]
    assert structure["type"] == "dict"
    assert set(structure["keys"]) == {"config", "processing", "validation"}


def test_cache_functionality(temp_doc_dir: Path):
    """Testa sistema de cache."""
    processor = DocumentProcessor(cache_ttl=1)  # 1 segundo TTL para teste
    md_file = temp_doc_dir / "test.md"

    # Primeira leitura - cache miss
    start_time = time.time()
    result1 = processor.process_file(md_file)
    first_process_time = time.time() - start_time

    # Segunda leitura imediata - cache hit
    start_time = time.time()
    result2 = processor.process_file(md_file)
    cached_process_time = time.time() - start_time

    # Verificar cache hit
    assert cached_process_time < first_process_time
    assert processor.stats["cache_hits"] == 1
    assert processor.stats["cache_misses"] == 1

    # Esperar expiração do cache
    time.sleep(1.1)

    # Terceira leitura - cache miss após expiração
    result3 = processor.process_file(md_file)
    assert processor.stats["cache_misses"] == 2


def test_file_monitoring(temp_doc_dir: Path):
    """Testa monitoramento de arquivos."""
    processor = DocumentProcessor()
    monitor = AIEnhancedMonitor(processor)

    events = []
    processed_files = set()

    def on_file_processed(file_path: str):
        processed_files.add(file_path)
        events.append(("processed", file_path))

    # Iniciar monitoramento em thread separada
    monitoring_thread = threading.Thread(target=monitor._run)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    try:
        # Criar novo arquivo
        test_file = temp_doc_dir / "new_doc.md"
        test_file.write_text(pytest.test_doc_content, encoding="utf-8")

        # Esperar processamento
        time.sleep(0.5)

        # Modificar arquivo
        test_file.write_text(
            pytest.test_doc_content + "\n## New Section", encoding="utf-8"
        )

        # Esperar processamento
        time.sleep(0.5)

        # Verificar estatísticas
        stats = monitor.get_stats()
        assert stats["events_processed"] > 0
        assert stats["files_monitored"] > 0

    finally:
        monitoring_thread.join(timeout=1)


def test_batch_processing(temp_doc_dir: Path):
    """Testa processamento em lote de diretório."""
    processor = DocumentProcessor()

    # Criar mais arquivos para teste
    (temp_doc_dir / "doc1.md").write_text(pytest.test_doc_content, encoding="utf-8")
    (temp_doc_dir / "doc2.md").write_text(pytest.test_doc_content, encoding="utf-8")
    (temp_doc_dir / "config1.yaml").write_text(
        pytest.test_yaml_content, encoding="utf-8"
    )

    # Processar diretório
    results = processor.process_directory(temp_doc_dir)

    # Verificar resultados
    assert len(results) == 4  # 4 arquivos processados
    assert all("error" not in result for result in results.values())
    assert processor.stats["processed_files"] == 4


def test_error_handling(temp_doc_dir: Path):
    """Testa tratamento de erros."""
    processor = DocumentProcessor()

    # Criar arquivo inválido
    invalid_yaml = temp_doc_dir / "invalid.yaml"
    invalid_yaml.write_text("invalid: [\n", encoding="utf-8")

    # Tentar processar arquivo inválido
    with pytest.raises(Exception):
        processor.process_file(invalid_yaml)

    assert processor.stats["errors"] == 1

    # Processar diretório com arquivo inválido
    results = processor.process_directory(temp_doc_dir)
    assert "error" in results[str(invalid_yaml)]


def test_thread_safety(temp_doc_dir: Path):
    """Testa thread-safety do processador."""
    processor = DocumentProcessor()
    md_file = temp_doc_dir / "test.md"

    def process_file():
        for _ in range(50):
            processor.process_file(md_file)

    # Criar múltiplas threads
    threads = [threading.Thread(target=process_file) for _ in range(4)]

    # Executar threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verificar consistência
    total_operations = processor.stats["cache_hits"] + processor.stats["cache_misses"]
    assert total_operations == 200  # 4 threads * 50 operações
    assert processor.stats["errors"] == 0

"""
Testes unitários para o módulo ai_processor.
"""

import tempfile
from pathlib import Path
from unittest import TestCase, main

import yaml
from watchdog.events import FileModifiedEvent

from src.ai_processor import AIEnhancedMonitor, DocProcessor


class TestDocProcessor(TestCase):
    """Testes para a classe DocProcessor."""

    def setUp(self):
        """Configuração dos testes."""
        self.processor = DocProcessor(cache_ttl=60)
        self.temp_dir = tempfile.mkdtemp()

    def test_process_markdown(self):
        """Testa processamento de arquivo markdown."""
        content = """---
title: Test Document
author: Test User
---
# Header 1
## Header 2
```python
def test():
    pass
```
"""
        filepath = Path(self.temp_dir) / "test.md"
        with open(filepath, "w") as f:
            f.write(content)

        result = self.processor.process_file(filepath)

        assert result["type"] == "markdown"
        assert len(result["headers"]) == 2
        assert result["code_blocks"] == 1
        assert result["metadata"]["title"] == "Test Document"

    def test_process_yaml(self):
        """Testa processamento de arquivo YAML."""
        content = """
version: 1.0
config:
  debug: true
  levels:
    - info
    - warning
    - error
"""
        filepath = Path(self.temp_dir) / "test.yaml"
        with open(filepath, "w") as f:
            f.write(content)

        result = self.processor.process_file(filepath)

        assert result["type"] == "yaml"
        assert result["structure"]["type"] == "dict"
        assert "config" in result["structure"]["nested"]

    def test_cache_functionality(self):
        """Testa funcionalidade de cache."""
        content = "# Test\nContent"
        filepath = Path(self.temp_dir) / "cache_test.md"
        with open(filepath, "w") as f:
            f.write(content)

        # Primeira leitura
        self.processor.process_file(filepath)
        self.processor.get_stats()

        # Segunda leitura (deve usar cache)
        self.processor.process_file(filepath)
        final_stats = self.processor.get_stats()

        assert final_stats["cache_hits"] == 1
        assert final_stats["processed_files"] == 1


class TestAIEnhancedMonitor(TestCase):
    """Testes para a classe AIEnhancedMonitor."""

    def setUp(self):
        """Configuração dos testes."""
        self.monitor = AIEnhancedMonitor(
            patterns=["*.md", "*.yaml"],
            ignore_patterns=["*.tmp"],
        )
        self.temp_dir = tempfile.mkdtemp()

    def test_file_monitoring(self):
        """Testa monitoramento de arquivos."""
        # Cria arquivo markdown
        md_path = Path(self.temp_dir) / "test.md"
        with open(md_path, "w") as f:
            f.write("# Test\nContent")

        # Simula evento de modificação
        event = FileModifiedEvent(str(md_path))
        self.monitor.on_modified(event)

        stats = self.monitor.get_stats()
        assert stats["events_processed"] == 1
        assert "markdown" in stats["patterns_detected"]

    def test_ignore_patterns(self):
        """Testa padrões de ignore."""
        # Cria arquivo temporário
        tmp_path = Path(self.temp_dir) / "test.tmp"
        with open(tmp_path, "w") as f:
            f.write("temporary content")

        # Simula evento de modificação
        event = FileModifiedEvent(str(tmp_path))
        self.monitor.on_modified(event)

        stats = self.monitor.get_stats()
        assert stats["events_processed"] == 0

    def test_pattern_matching(self):
        """Testa correspondência de padrões."""
        # Cria arquivo YAML
        yaml_path = Path(self.temp_dir) / "config.yaml"
        content = {"test": True}
        with open(yaml_path, "w") as f:
            yaml.dump(content, f)

        # Simula evento de modificação
        event = FileModifiedEvent(str(yaml_path))
        self.monitor.on_modified(event)

        stats = self.monitor.get_stats()
        assert stats["events_processed"] == 1
        assert "yaml" in stats["patterns_detected"]


if __name__ == "__main__":
    main()

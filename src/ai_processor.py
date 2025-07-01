"""
Processador de documentação com recursos de IA para o sistema DOCSYNC.
Fornece análise, sugestões e melhorias para documentação técnica.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class DocumentProcessor:
    """Processador principal de documentos com recursos de IA."""

    def __init__(self, config_path: Optional[Path] = None):
        """Inicializa o processador de documentos."""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.cache = {}
        self.history = []

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Carrega configurações do processador."""
        default_config = {
            "analysis_enabled": True,
            "suggestion_threshold": 0.7,
            "cache_ttl": 3600,
            "max_suggestions": 5,
            "languages": ["pt_BR", "en"],
            "doc_types": ["technical", "api", "architecture"],
        }

        if config_path and config_path.exists():
            with open(config_path) as f:
                custom_config = yaml.safe_load(f)
                return {**default_config, **custom_config}
        return default_config

    def analyze_document(self, doc_path: Path) -> Dict:
        """Analisa documento e fornece insights."""
        self.logger.info(f"Analisando documento: {doc_path}")

        # Verificar cache
        cache_key = f"{doc_path}:{doc_path.stat().st_mtime}"
        if cache_key in self.cache:
            self.logger.debug("Usando resultado em cache")
            return self.cache[cache_key]

        try:
            content = doc_path.read_text()
            metadata, body = self._extract_metadata(content)

            analysis = {
                "metadata": metadata,
                "stats": self._analyze_stats(body),
                "quality": self._assess_quality(body),
                "suggestions": self._generate_suggestions(body, metadata),
                "timestamp": datetime.now().isoformat(),
            }

            # Atualizar cache
            self.cache[cache_key] = analysis
            return analysis

        except Exception as e:
            self.logger.error(f"Erro ao analisar documento: {e}")
            raise

    def _extract_metadata(self, content: str) -> Tuple[Dict, str]:
        """Extrai e valida metadados do documento."""
        try:
            parts = content.split("---")
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                body = "---".join(parts[2:]).strip()
            else:
                metadata = {}
                body = content

            return metadata, body

        except Exception as e:
            self.logger.error(f"Erro ao extrair metadados: {e}")
            return {}, content

    def _analyze_stats(self, content: str) -> Dict:
        """Analisa estatísticas do documento."""
        words = content.split()
        sentences = content.split(".")

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "sections": content.count("#"),
            "code_blocks": content.count("```"),
        }

    def _assess_quality(self, content: str) -> Dict:
        """Avalia qualidade do documento."""
        quality_metrics = {
            "completeness": self._check_completeness(content),
            "clarity": self._analyze_clarity(content),
            "structure": self._evaluate_structure(content),
            "code_quality": self._check_code_quality(content),
        }

        return {
            "metrics": quality_metrics,
            "score": sum(quality_metrics.values()) / len(quality_metrics),
            "timestamp": datetime.now().isoformat(),
        }

    def _check_completeness(self, content: str) -> float:
        """Verifica completude do documento."""
        required_sections = ["# ", "## ", "Example", "Usage"]
        present_sections = sum(1 for section in required_sections if section in content)
        return present_sections / len(required_sections)

    def _analyze_clarity(self, content: str) -> float:
        """Analisa clareza do documento."""
        words = content.split()
        complex_words = len([w for w in words if len(w) > 12])
        clarity_score = 1 - (complex_words / len(words) if words else 0)
        return min(max(clarity_score, 0), 1)

    def _evaluate_structure(self, content: str) -> float:
        """Avalia estrutura do documento."""
        lines = content.split("\n")
        section_levels = [line.count("#") for line in lines if line.startswith("#")]

        if not section_levels:
            return 0.0

        # Verificar hierarquia adequada
        is_hierarchical = all(
            a <= b for a, b in zip(section_levels, section_levels[1:])
        )
        has_title = 1 in section_levels
        has_subsections = len(set(section_levels)) > 1

        return sum([is_hierarchical, has_title, has_subsections]) / 3

    def _check_code_quality(self, content: str) -> float:
        """Avalia qualidade dos blocos de código."""
        code_blocks = content.split("```")[1::2]  # Pegar apenas conteúdo entre ```
        if not code_blocks:
            return 1.0  # Se não há código, não penalizar

        metrics = []
        for block in code_blocks:
            # Verificar indentação consistente
            lines = block.split("\n")
            if len(lines) > 1:
                indentation_consistent = (
                    len(
                        set(
                            len(line) - len(line.lstrip())
                            for line in lines
                            if line.strip()
                        )
                    )
                    <= 2
                )
                metrics.append(1.0 if indentation_consistent else 0.5)

            # Verificar presença de comentários
            has_comments = any(line.strip().startswith(("#", "//")) for line in lines)
            metrics.append(1.0 if has_comments else 0.7)

        return sum(metrics) / len(metrics) if metrics else 1.0

    def _generate_suggestions(self, content: str, metadata: Dict) -> List[Dict]:
        """Gera sugestões de melhoria para o documento."""
        suggestions = []

        # Verificar metadados
        if not metadata.get("title"):
            suggestions.append(
                {
                    "type": "metadata",
                    "severity": "high",
                    "message": "Adicionar título ao documento",
                    "context": "Metadados incompletos",
                }
            )

        if not metadata.get("version"):
            suggestions.append(
                {
                    "type": "metadata",
                    "severity": "medium",
                    "message": "Especificar versão do documento",
                    "context": "Controle de versão",
                }
            )

        # Analisar estrutura
        if not content.startswith("# "):
            suggestions.append(
                {
                    "type": "structure",
                    "severity": "high",
                    "message": "Iniciar documento com título principal (h1)",
                    "context": "Estrutura do documento",
                }
            )

        # Verificar seções comuns
        common_sections = ["## Overview", "## Installation", "## Usage", "## Examples"]
        missing_sections = [
            section
            for section in common_sections
            if section.lower() not in content.lower()
        ]

        if missing_sections:
            suggestions.append(
                {
                    "type": "content",
                    "severity": "medium",
                    "message": f'Considerar adicionar seções: {", ".join(missing_sections)}',
                    "context": "Completude do documento",
                }
            )

        # Analisar blocos de código
        code_blocks = content.count("```")
        if code_blocks > 0 and content.count("Example") == 0:
            suggestions.append(
                {
                    "type": "content",
                    "severity": "medium",
                    "message": "Adicionar seção de exemplos para contextualizar blocos de código",
                    "context": "Exemplos e código",
                }
            )

        return suggestions[: self.config["max_suggestions"]]

    def process_directory(self, dir_path: Path) -> Dict[str, Dict]:
        """Processa todos os documentos em um diretório."""
        self.logger.info(f"Processando diretório: {dir_path}")
        results = {}

        try:
            for doc_path in dir_path.glob("**/*.md"):
                try:
                    results[str(doc_path)] = self.analyze_document(doc_path)
                except Exception as e:
                    self.logger.error(f"Erro ao processar {doc_path}: {e}")
                    results[str(doc_path)] = {"error": str(e)}

            return results

        except Exception as e:
            self.logger.error(f"Erro ao processar diretório: {e}")
            raise

    def export_analysis(self, analysis: Dict, output_path: Path):
        """Exporta resultados da análise em formato estruturado."""
        try:
            output = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "config_version": self.config.get("version", "1.0"),
            }

            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            self.logger.info(f"Análise exportada para: {output_path}")

        except Exception as e:
            self.logger.error(f"Erro ao exportar análise: {e}")
            raise


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Exemplo de uso
    processor = DocumentProcessor()
    test_doc = Path("example/test.md")

    if test_doc.exists():
        analysis = processor.analyze_document(test_doc)
        print(json.dumps(analysis, indent=2))

"""
AI-enhanced document processing and monitoring module.
Handles markdown and YAML file processing with caching and intelligent monitoring.
"""

import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Set, Tuple

import yaml
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DocProcessor:
    """Processes documents with caching and metadata extraction."""

    def __init__(self, cache_ttl: int = 3600):
        self.cache: Dict[str, Tuple[float, dict]] = {}  # path -> (timestamp, data)
        self.cache_ttl = cache_ttl
        self.cache_lock = Lock()
        self.stats = {
            "processed_files": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
        }

    def process_file(self, file_path: str) -> Optional[dict]:
        """Process a file with caching."""
        try:
            current_time = time.time()

            # Check cache first
            with self.cache_lock:
                if file_path in self.cache:
                    timestamp, data = self.cache[file_path]
                    if current_time - timestamp < self.cache_ttl:
                        self.stats["cache_hits"] += 1
                        return data
                self.stats["cache_misses"] += 1

            # Process file based on extension
            if file_path.endswith(".md"):
                result = self._process_markdown(file_path)
            elif file_path.endswith((".yaml", ".yml")):
                result = self._process_yaml(file_path)
            else:
                return None

            # Update cache
            with self.cache_lock:
                self.cache[file_path] = (current_time, result)

            self.stats["processed_files"] += 1
            return result

        except Exception as e:
            self.stats["errors"] += 1
            raise Exception(f"Error processing {file_path}: {str(e)}")

    def _process_markdown(self, file_path: str) -> dict:
        """Extract metadata, headers and code blocks from markdown."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata (YAML frontmatter)
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)[1:]
            if len(parts) >= 1:
                try:
                    metadata = yaml.safe_load(parts[0])
                except:
                    pass

        # Extract headers
        headers = []
        for line in content.split("\n"):
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("#").strip()
                headers.append({"level": level, "text": text})

        # Extract code blocks
        code_blocks = []
        code_pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
        for match in code_pattern.finditer(content):
            lang, code = match.groups()
            code_blocks.append({"language": lang or "text", "code": code.strip()})

        return {
            "metadata": metadata,
            "headers": headers,
            "code_blocks": code_blocks,
            "file_path": file_path,
            "last_modified": os.path.getmtime(file_path),
        }

    def _process_yaml(self, file_path: str) -> dict:
        """Process YAML files with structure analysis."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)

        def analyze_structure(data, path="root"):
            if isinstance(data, dict):
                return {
                    "type": "dict",
                    "keys": list(data.keys()),
                    "children": {
                        k: analyze_structure(v, f"{path}.{k}") for k, v in data.items()
                    },
                }
            elif isinstance(data, list):
                return {
                    "type": "list",
                    "length": len(data),
                    "sample": (
                        analyze_structure(data[0], f"{path}[0]") if data else None
                    ),
                }
            else:
                return {"type": type(data).__name__, "path": path}

        return {
            "content": content,
            "structure": analyze_structure(content),
            "file_path": file_path,
            "last_modified": os.path.getmtime(file_path),
        }

    def get_stats(self) -> dict:
        """Return processing statistics."""
        return self.stats.copy()


class AIEnhancedMonitor(FileSystemEventHandler):
    """Intelligent file monitoring with pattern detection."""

    def __init__(self, processor: DocProcessor, patterns: Set[str] = None):
        self.processor = processor
        self.patterns = patterns or {".md", ".yaml", ".yml"}
        self.file_history: Dict[str, List[float]] = {}
        self.stats = {
            "events_processed": 0,
            "files_monitored": 0,
            "patterns_detected": 0,
        }
        self._lock = Lock()

    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification events."""
        if not event.is_directory and self._should_process(event.src_path):
            with self._lock:
                self.stats["events_processed"] += 1

                # Track file modifications
                path = event.src_path
                current_time = time.time()
                if path not in self.file_history:
                    self.file_history[path] = []
                    self.stats["files_monitored"] += 1

                self.file_history[path].append(current_time)

                # Clean old history
                self.file_history[path] = [
                    t for t in self.file_history[path] if current_time - t < 3600
                ]

                # Detect patterns
                if len(self.file_history[path]) >= 3:
                    self.stats["patterns_detected"] += 1

                # Process file
                try:
                    self.processor.process_file(path)
                except Exception as e:
                    print(f"Error processing {path}: {str(e)}")

    def _should_process(self, path: str) -> bool:
        """Check if file should be processed based on extension."""
        return any(path.endswith(pat) for pat in self.patterns)

    def get_stats(self) -> dict:
        """Return monitoring statistics."""
        with self._lock:
            stats = self.stats.copy()
            stats["processor_stats"] = self.processor.get_stats()
            return stats


def setup_monitoring(
    path: str, patterns: Set[str] = None
) -> Tuple[Observer, AIEnhancedMonitor]:
    """Set up file monitoring for a directory."""
    processor = DocProcessor()
    monitor = AIEnhancedMonitor(processor, patterns)

    observer = Observer()
    observer.schedule(monitor, path, recursive=True)
    observer.start()

    return observer, monitor

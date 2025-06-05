"""
Exemplo de uso do processador de documentos com IA do DOCSYNC.
"""

import logging
from pathlib import Path
from src.ai_processor import DocProcessor, AIEnhancedMonitor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Demonstra o uso do processador de documentos."""
    try:
        # Inicializar processador
        doc_processor = DocProcessor()
        monitor = AIEnhancedMonitor(doc_processor)
        
        # Exemplo de processamento de diferentes tipos de arquivo
        docs_dir = Path("docs")
        test_files = [
            docs_dir / "example.md",
            docs_dir / "config.yaml",
            docs_dir / "data.json"
        ]
        
        for file_path in test_files:
            if file_path.exists():
                logger.info(f"\nProcessando {file_path}")
                try:
                    # Simular evento de arquivo modificado
                    result = monitor.process_file_event("modified", file_path)
                    logger.info(f"Resultado: {result}")
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")
        
        # Exibir estatísticas
        logger.info("\nEstatísticas de Monitoramento:")
        monitoring_stats = monitor.get_monitoring_stats()
        logger.info(f"Total de eventos: {monitoring_stats.get('total_events', 0)}")
        logger.info(f"Taxa de sucesso: {monitoring_stats.get('success_rate', 0):.2%}")
        
        logger.info("\nEstatísticas de Aprendizado:")
        learning_stats = doc_processor.get_learning_stats()
        logger.info(f"Total de documentos: {learning_stats.get('total_documents', 0)}")
        logger.info(f"Tipos de documento: {learning_stats.get('document_types', {})}")
        
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")

if __name__ == "__main__":
    main()


import pytest
import yaml
import time
from pathlib import Path
from docsync.core import DocSync, DocSyncEventHandler

@pytest.fixture
def test_config():
    """Fixture que fornece uma configuração de teste básica."""
    return {
        'templates': {
            'default_path': 'templates',
            'extensions': ['.md', '.rst']
        },
        'monitoring': {
            'patterns': ['*.md', '*.rst'],
            'ignore_patterns': ['.*', '~*'],
            'recursive': True
        },
        'sync': {
            'auto_sync': True,
            'interval': 300,
            'max_retries': 3
        }
    }

@pytest.fixture
def test_dir(tmp_path):
    """Cria uma estrutura de diretório temporária para testes."""
    docs_dir = tmp_path / "docs"
    templates_dir = tmp_path / "templates"
    
    # Cria diretórios
    docs_dir.mkdir()
    templates_dir.mkdir()
    
    # Cria arquivo de template de teste
    test_template = templates_dir / "test_template.md"
    test_template.write_text("# {{ title }}\n\n{{ content }}")
    
    # Cria arquivo de configuração
    config_file = docs_dir / "docsync.yaml"
    config = {
        'templates_path': str(templates_dir),
        'patterns': ['*.md', '*.rst']
    }
    config_file.write_text(yaml.dump(config))
    
    return docs_dir

@pytest.fixture
def docsync(test_dir, test_config):
    """Inicializa uma instância do DocSync para testes."""
    return DocSync(base_path=test_dir)

def test_docsync_initialization(docsync, test_dir):
    """Testa a inicialização correta do DocSync."""
    assert docsync.base_path == test_dir
    assert docsync.config_path == test_dir / "docsync.yaml"
    assert docsync.templates_path == test_dir / "templates"
    assert isinstance(docsync.config, dict)
    assert docsync.logger is not None

def test_config_loading(test_dir, test_config):
    """Testa o carregamento da configuração do arquivo."""
    config_file = test_dir / "docsync.yaml"
    config_file.write_text(yaml.dump(test_config))
    
    docsync = DocSync(base_path=test_dir)
    assert docsync.config == test_config

def test_monitoring_lifecycle(docsync):
    """Testa o ciclo de vida do monitoramento."""
    # Inicia monitoramento
    docsync.start_monitoring()
    assert docsync.observer.is_alive()
    
    # Para monitoramento
    docsync.stop_monitoring()
    assert not docsync.observer.is_alive()

def test_file_event_handling(docsync, test_dir):
    """Testa o tratamento de eventos de arquivo."""
    # Inicia monitoramento
    docsync.start_monitoring()
    
    try:
        # Cria arquivo de teste
        test_file = test_dir / "test_document.md"
        test_file.write_text("# Test Document")
        
        # Aguarda processamento do evento
        time.sleep(1)
        
        # Modifica arquivo
        test_file.write_text("# Modified Test Document")
        
        # Aguarda processamento do evento
        time.sleep(1)
        
        # Remove arquivo
        test_file.unlink()
        
        # Aguarda processamento do evento
        time.sleep(1)
        
    finally:
        docsync.stop_monitoring()

def test_create_document_with_template(docsync, test_dir):
    """Testa a criação de documento usando template."""
    template_name = "test_template"
    target_path = test_dir / "new_document.md"
    
    # Cria template de teste
    template_file = docsync.templates_path / f"{template_name}.md"
    template_file.write_text("# {{ title }}\n\n{{ content }}")
    
    # Testa criação do documento
    docsync.create_document(
        template_name,
        target_path,
        title="Test Title",
        content="Test Content"
    )
    
    assert target_path.exists()

def test_create_document_without_template(docsync, test_dir):
    """Testa erro ao criar documento sem template."""
    target_path = test_dir / "error_document.md"
    
    with pytest.raises(FileNotFoundError):
        docsync.create_document("non_existent", target_path)

def test_sync_documents(docsync, test_dir):
    """Testa sincronização de documentos."""
    # Cria alguns arquivos de teste
    doc1 = test_dir / "doc1.md"
    doc2 = test_dir / "doc2.md"
    
    doc1.write_text("# Document 1")
    doc2.write_text("# Document 2")
    
    # Executa sincronização
    docsync.sync_documents()
    
    # TODO: Adicionar verificações específicas quando a
    # funcionalidade de sincronização for implementada

def test_event_handler_initialization(docsync):
    """Testa inicialização do handler de eventos."""
    handler = DocSyncEventHandler(docsync)
    assert handler.docsync == docsync
    assert handler.logger == docsync.logger

@pytest.mark.parametrize("event_type", ["created", "modified", "deleted"])
def test_event_handler_methods(docsync, test_dir, event_type):
    """Testa métodos do handler de eventos."""
    handler = DocSyncEventHandler(docsync)
    
    # Cria um mock de evento
    class MockEvent:
        is_directory = False
        src_path = str(test_dir / "test_file.md")
    
    # Testa cada tipo de evento
    event = MockEvent()
    method = getattr(handler, f"on_{event_type}")
    method(event)  # Não deve levantar exceções

def test_logging_configuration(docsync):
    """Testa configuração de logging."""
    assert docsync.logger.name == "docsync"
    assert len(docsync.logger.handlers) > 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])


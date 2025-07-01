# Guia Rápido - docsync para GUARDRIVE

Este guia fornece os passos essenciais para começar a usar o sistema de sincronização de documentação GUARDRIVE.

## Instalação em 5 Minutos

1. Clone e prepare o ambiente:
   ```bash
   git clone https://github.com/seu-usuario/docsync.git
   cd docsync
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. Configure a sincronização:
   ```bash
   # Copie o arquivo de exemplo
   cp guardrive_sync.yaml.example guardrive_sync.yaml
   
   # Edite com seu editor preferido
   notepad guardrive_sync.yaml  # Windows
   nano guardrive_sync.yaml     # Linux/macOS
   ```

3. Inicie o sistema:
   ```bash
   python run_sync.py
   ```

## Configuração Mínima

Exemplo de configuração básica (guardrive_sync.yaml):

```yaml
# Configuração essencial
guardrive:
  enabled: true
  base_path: "C:/Users/SEU_USUARIO/GUARDRIVE/GUARDRIVE_V1/1. GUARDRIVE_DOCS_DEV"
  docs_path: "GUARDRIVE_DOCS"
  dev_path: "2.AREA_DEV"
  
  # Mapeamento mínimo
  path_mappings:
    - source_path: "GUARDRIVE_DOCS/01_TECHNICAL"
      target_path: "2.AREA_DEV/04_Material DEV#1"
      doc_type: "technical"
      bidirectional: true

# Sincronização
sync:
  real_time_sync: true
  sync_interval: 300
```

## Casos de Uso Comuns

1. **Sincronização Manual**
   ```bash
   # Sincronização única
   python run_sync.py --config guardrive_sync.yaml
   ```

2. **Monitoramento Contínuo**
   ```bash
   # Inicia monitoramento em tempo real
   python run_sync.py -v
   ```

3. **Verificação de Status**
   ```bash
   # Mostra estado atual da sincronização
   python run_sync.py --status
   ```

## Estrutura de Diretórios

```
GUARDRIVE_V1/
├── 1. GUARDRIVE_DOCS_DEV/
│   ├── GUARDRIVE_DOCS/        # Documentação oficial
│   │   ├── 01_TECHNICAL/     # Docs técnicos
│   │   └── 02_BUSINESS/      # Docs de negócio
│   └── 2.AREA_DEV/           # Área de desenvolvimento
│       └── 04_Material DEV#1/ # Docs em desenvolvimento
```

## Solução Rápida de Problemas

1. **Erro de Permissão**
   ```bash
   # Verifique permissões
   icacls "C:\Users\SEU_USUARIO\GUARDRIVE" /T
   ```

2. **Falha na Sincronização**
   - Verifique caminhos no guardrive_sync.yaml
   - Confirme que os diretórios existem
   - Verifique logs em %APPDATA%/docsync/logs

3. **Erros de Git**
   ```bash
   # Reinicie repositório Git
   cd seu/diretorio/guardrive
   git init
   ```

## Dicas Essenciais

1. **Backup Automático**
   - Ative no arquivo de configuração:
   ```yaml
   guardrive:
     version_control:
       backup_enabled: true
       backup_interval: 3600  # 1 hora
   ```

2. **Monitoramento**
   - Verifique logs em tempo real:
   ```bash
   python run_sync.py -v --log-level DEBUG
   ```

3. **Performance**
   - Use ignore_patterns para arquivos desnecessários:
   ```yaml
   sync:
     ignore_patterns: [".git", "*.tmp", "*.bak"]
   ```

## Próximos Passos

- Consulte README.md para configurações avançadas
- Configure integrações Git adicionais
- Explore recursos de validação de documentos
- Configure backup remoto

## Suporte Rápido

- Logs: `%APPDATA%/docsync/logs`
- Configuração: `guardrive_sync.yaml`
- Documentação: `docs/`


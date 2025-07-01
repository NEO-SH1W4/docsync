# DOCSYNC

## Visão Geral
DOCSYNC é um sistema avançado de sincronização de documentação que implementa protocolos quantum-secure, validações metacognitivas e monitoramento em tempo real. O projeto visa garantir a integridade e consistência da documentação através de múltiplas dimensões de realidade.

## Características Principais
- Sincronização quântica instantânea
- Validação metacognitiva
- Monitoramento em tempo real
- Segurança quantum-resistant
- Auditoria contínua

## 📊 Análise de Mercado

Para uma análise completa do potencial de mercado, custos de desenvolvimento e viabilidade do projeto, consulte:
- **[Análise de Mercado e Viabilidade - DOCSYNC](./ANALISE_MERCADO_VIABILIDADE.md)** - Documento detalhado com estimativas de tempo, custos, projeções de receita e análise competitiva
- **[Template de Análise de Mercado](./templates/business/TEMPLATE_ANALISE_MERCADO.md)** - Template genérico para análises similares de outros projetos

### Resumo Executivo da Análise:
- **Mercado Total Addressable:** $45+ bilhões
- **Investimento Necessário:** ~$1.6M para desenvolvimento completo
- **Tempo para MVP:** 4-6 meses
- **Break-even Projetado:** Ano 2-3
- **ROI Estimado (5 anos):** 450-1,200%

## Requisitos
- Python >= 3.9
- Git
- Dependências adicionais listadas em pyproject.toml

## Instalação

```powershell
# Clone o repositório
git clone https://github.com/NEO-SH1W4/DOCSYNC.git
cd DOCSYNC

# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate

# Instale as dependências
pip install -e .
```

## Uso Básico
(Documentação em desenvolvimento)

## Desenvolvimento

### Setup do Ambiente
1. Clone o repositório
2. Configure o ambiente virtual
3. Instale as dependências de desenvolvimento
4. Execute os testes

### Testes
```powershell
pytest
```

### Linting
```powershell
flake8
```

## Contribuição
1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença
[MIT](https://choosealicense.com/licenses/mit/)

## Contato
- NEO-SH1W4
- Link do Projeto: [https://github.com/NEO-SH1W4/DOCSYNC](https://github.com/NEO-SH1W4/DOCSYNC)

# DOCSYNC

Sistema de sincronização bidirecional entre arquivos locais e Notion.

## Instalação

1. Ambiente de desenvolvimento:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt
```

2. Ambiente de produção:
```bash
pip install -r requirements.txt
```

## Testes

Execute os testes com:
```bash
pytest
```

Para verificar cobertura:
```bash
pytest --cov=docsync
```

## Qualidade de Código

1. Formatação:
```bash
black .
isort .
```

2. Verificação:
```bash
flake8
mypy .
```

## Contribuindo

1. Certifique-se de ter todas as dependências de desenvolvimento instaladas
2. Execute os testes antes de submeter alterações
3. Mantenha 100% de cobertura de testes
4. Siga as convenções de código do projeto

# Notion Integration Guide

## Overview

A integração DOCSYNC-Notion permite sincronização bidirecional entre seus documentos locais e o Notion, oferecendo:

- Sincronização automática de documentação
- Versionamento unificado
- Análise de qualidade em tempo real
- Backup automatizado
- Colaboração aprimorada

## Configuração

1. **Token do Notion**
   - Acesse https://www.notion.so/my-integrations
   - Crie uma nova integração
   - Copie o token gerado

2. **Configuração Básica**
   `ash
   # Inicializar configuração
   python examples/notion/notion_cli.py init --token seu_token_aqui

   # Edite o arquivo notion_config.json gerado
   `

3. **Estrutura do notion_config.json**
   `json
   {
     'token': 'seu_token_aqui',
     'workspace_id': 'seu_workspace_id',
     'mappings': [
       {
         'source_path': './docs/technical',
         'target_id': 'id_database_notion',
         'sync_type': 'bidirectional'
       }
     ],
     'sync_interval': 300,
     'max_retries': 3,
     'retry_delay': 60
   }
   `

## Uso

1. **Sincronização via CLI**
   `ash
   # Sincronizar usando arquivo de configuração
   python examples/notion/notion_cli.py sync -c notion_config.json

   # Sincronização direta
   python examples/notion/notion_cli.py sync --token seu_token --source ./docs --target id_database
   `

2. **Sincronização Programática**
   `python
   from docsync.integrations.notion import NotionBridge, NotionConfig, NotionMapping
   from pathlib import Path

   config = NotionConfig(
       token='seu_token',
       workspace_id='seu_workspace',
       mappings=[
           NotionMapping(
               source_path=Path('./docs'),
               target_id='id_database'
           )
       ]
   )

   bridge = NotionBridge(config)
   await bridge.initialize()
   await bridge.sync()
   `

## Monitoramento Contínuo

Para manter a sincronização contínua:

`ash
# Usar o exemplo de sincronização contínua
python examples/notion/notion_sync_example.py
`

## Recursos Avançados

1. **Filtragem de Conteúdo**
   `python
   NotionMapping(
       source_path=Path('./docs'),
       target_id='id_database',
       filters=['*.md', '!temp/*']
   )
   `

2. **Tipos de Sincronização**
   - bidirectional: Sincroniza em ambas as direções
   - push: Apenas envia para o Notion
   - pull: Apenas recebe do Notion

## Troubleshooting

1. **Verificar Configuração**
   `ash
   python examples/notion/notion_cli.py validate -c notion_config.json
   `

2. **Logs**
   - Os logs são salvos em .notion_sync em cada diretório mapeado
   - Use --verbose para mais detalhes durante a sincronização

## Boas Práticas

1. **Estrutura de Diretórios**
   - Mantenha uma estrutura clara e organizada
   - Use subdiretórios para diferentes tipos de documentação

2. **Versionamento**
   - Mantenha o arquivo .notion_sync no controle de versão
   - Não compartilhe tokens de acesso

3. **Backup**
   - A integração mantém backups automáticos
   - Configure ackup_interval conforme necessidade

## Limitações

1. **Rate Limits**
   - A API do Notion tem limites de requisição
   - A integração gerencia automaticamente os limites

2. **Formatos Suportados**
   - Markdown (*.md)
   - Futuramente: RST, AsciiDoc

## Integração com CI/CD

Exemplo de uso em pipeline CI/CD:

`yaml
jobs:
  sync-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python examples/notion/notion_cli.py sync -c notion_config.json
        env:
          NOTION_TOKEN: 
`
"@ | Out-File -Encoding utf8 examples\notion\GUIDE.md

@"
# DOCSYNC

Sistema avançado de sincronização e gerenciamento de documentação técnica.

## Novidade: Integração com Notion! 🎉

Agora o DOCSYNC oferece integração completa com o Notion, permitindo:
- Sincronização bidirecional de documentação
- Análise de qualidade em tempo real
- Versionamento unificado
- Colaboração aprimorada

[Veja o guia completo da integração com Notion](examples/notion/GUIDE.md)

## Recursos Principais

- Sincronização inteligente de documentação
- Processamento AI-enhanced de documentos
- Integração com múltiplas plataformas
- Sistema de templates flexível
- Análise de qualidade automática
- Versionamento robusto

## Integrações Suportadas

- Notion (Nova!)
- Git Repositories
- Markdown Files
- API Documentation
- Technical Specifications

## Instalação

`ash
pip install docsync
`

## Uso Rápido

1. **Configuração Básica**
   `python
   from docsync import DocSync
   
   sync = DocSync()
   sync.configure()
   `

2. **Sincronização com Notion**
   `python
   from docsync.integrations.notion import NotionBridge, NotionConfig
   
   config = NotionConfig(token='seu_token', workspace_id='seu_workspace')
   bridge = NotionBridge(config)
   await bridge.sync()
   `

3. **Processamento de Documentos**
   `python
   from docsync import DocumentProcessor
   
   processor = DocumentProcessor()
   analysis = processor.analyze_document('doc.md')
   `

## Documentação

- [Guia de Início Rápido](docs/quickstart.md)
- [Integração com Notion](examples/notion/GUIDE.md)
- [Documentação Completa](docs/index.md)
- [Exemplos](examples/)

## Contribuição

Contribuições são bem-vindas! Veja nosso [Guia de Contribuição](CONTRIBUTING.md).

## Licença

MIT License - veja [LICENSE](LICENSE) para mais detalhes.

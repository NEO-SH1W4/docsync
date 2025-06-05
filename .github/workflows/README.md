# CI/CD Workflows

Este diretório contém as configurações de automação para o projeto DOCSYNC.

## Workflows

### `test.yml`

Pipeline de testes automatizados que:

1. Executa em múltiplas versões do Python (3.9, 3.10, 3.11)
2. Verifica qualidade do código:
   - Execução de testes
   - Cobertura de código
   - Formatação
   
3. Gera e publica relatórios:
   - Cobertura (Codecov)
   - Resultados de teste (GitHub Actions)
   - Notificações (Slack)

### Variáveis de Ambiente Necessárias

Configure os seguintes secrets no GitHub:

- `NOTION_TEST_TOKEN`: Token de API do Notion para testes
- `NOTION_TEST_WORKSPACE`: ID do workspace de teste
- `SLACK_WEBHOOK_URL`: URL do webhook do Slack para notificações

### Artefatos Gerados

- Relatório de cobertura HTML
- Arquivo XML com resultados dos testes
- Relatório de cobertura XML para Codecov

### Requisitos Mínimos

- Cobertura de código: 80%
- Todos os testes passando
- Formatação de código correta


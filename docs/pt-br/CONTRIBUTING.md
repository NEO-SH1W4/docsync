# Contribuindo com o DocSync

Primeiramente, obrigado por considerar contribuir com o DocSync! 🎉

Este documento fornece diretrizes e informações importantes para contribuir com o projeto.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)
- [Pull Requests](#pull-requests)
- [Estilo de Código](#estilo-de-código)
- [Commits](#commits)
- [Testes](#testes)
- [Setup de Desenvolvimento](#setup-de-desenvolvimento)
- [Recursos Úteis](#recursos-úteis)

## 📜 Código de Conduta

Este projeto segue um Código de Conduta que todos os contribuidores devem observar. Por favor, leia [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 🤝 Como Posso Contribuir?

### 🐛 Reportando Bugs

1. Verifique se o bug já não foi reportado
2. Use o template de issue para bugs
3. Inclua passos detalhados para reprodução
4. Forneça informações do ambiente (OS, Python version, etc.)
5. Adicione logs e screenshots relevantes

### 💡 Sugerindo Melhorias

1. Primeiro discuta a melhoria via issue
2. Use o template de feature request
3. Descreva o problema que sua sugestão resolve
4. Explique como sua sugestão beneficia o projeto
5. Inclua exemplos de uso
6. Considere compatibilidade retroativa

## 🔄 Pull Requests

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Implemente suas mudanças
4. Adicione ou atualize testes
5. Atualize a documentação
6. Execute os testes (`pytest`)
7. Commit usando mensagens claras
8. Push para sua branch (`git push origin feature/MinhaFeature`)
9. Abra um Pull Request

### Checklist PR

- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Código formatado (black)
- [ ] Imports ordenados (isort)
- [ ] Tipos verificados (mypy)
- [ ] Changelog atualizado
- [ ] Versão incrementada se necessário
- [ ] 100% de cobertura em código novo

## 💻 Estilo de Código

### Python

- Use Python 3.9+
- Seguimos [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usamos [Black](https://black.readthedocs.io/) para formatação
- Tipos estáticos com [mypy](http://mypy-lang.org/)
- Docstrings no formato Google
- Type hints em todas as funções

```python
def calculate_metric(value: float, target: float) -> float:
    """Calcula a diferença percentual entre valor e meta.

    Args:
        value: Valor atual da métrica
        target: Valor alvo da métrica

    Returns:
        float: Diferença percentual

    Raises:
        ValueError: Se target for zero
    """
    if target == 0:
        raise ValueError("Target cannot be zero")
    return (value - target) / target * 100
```

### Imports

Usamos `isort` com as seguintes configurações:

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
```

## 📝 Commits

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

Exemplo:
```
feat(templates): Adiciona suporte a temas customizados

- Implementa sistema de temas
- Adiciona documentação
- Inclui testes
```

## ✅ Testes

- Use `pytest` para testes
- Mantenha cobertura acima de 80%
- Inclua testes de integração quando necessário
- Use fixtures para código repetitivo
- Mocks para recursos externos

```python
@pytest.fixture
def doc_sync():
    """Fixture que fornece instância configurada do DocSync."""
    return DocSync(templates_path="tests/fixtures/templates")

def test_generate_report(doc_sync):
    """Testa geração básica de relatório."""
    result = doc_sync.generate_report(
        template_name="test",
        data={"title": "Test"}
    )
    assert result.success
```

## 🛠️ Setup de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/docsync.git
cd docsync

# Crie e ative ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Instale dependências
pip install -e ".[dev]"

# Instale pre-commit hooks
pre-commit install

# Execute testes
pytest
```

## 📦 Gestão de Dependências

- Use `pyproject.toml` para dependências
- Mantenha dependências atualizadas
- Documente breaking changes

## 🔍 Processo de Review

1. Dois aprovadores necessários
2. CI deve passar
3. Documentação atualizada
4. Cobertura de testes mantida/melhorada

## 📚 Recursos Úteis

- [Documentação](https://docsync.readthedocs.io)
- [Issues](https://github.com/seu-usuario/docsync/issues)
- [Pull Requests](https://github.com/seu-usuario/docsync/pulls)
- [Changelog](CHANGELOG.md)

## ❓ Dúvidas?

- Abra uma issue
- Envie um email para dev@example.com
- Consulte a documentação

Obrigado por contribuir! 🎉

# Contribuindo para o DocSync

Primeiramente, obrigado por considerar contribuir para o DocSync! 🎉

## Como Contribuir

### Reportando Bugs
1. Verifique se o bug já não foi reportado
2. Abra uma issue clara e descritiva
3. Inclua passos para reprodução
4. Adicione logs e screenshots relevantes

### Sugerindo Melhorias
1. Primeiro discuta a melhoria via issue
2. Explique o comportamento atual e o desejado
3. Inclua exemplos de uso
4. Considere compatibilidade retroativa

### Código
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/sua-feature`)
3. Implemente suas mudanças
4. Adicione ou atualize testes
5. Atualize a documentação
6. Commit usando mensagens claras
7. Push para seu fork
8. Abra um Pull Request

## Padrões de Código

### Python
- Use Python 3.9+
- Siga PEP 8
- Docstrings em todas as funções/classes
- Type hints em todas as funções
- 100% de cobertura em código novo

### Testes
- Pytest para testes
- Fixtures reutilizáveis
- Mocks para recursos externos
- Testes de integração quando necessário

### Documentação
- Docstrings completas
- README atualizado
- Exemplos práticos
- Comentários claros e necessários

## Processo de Review
1. Dois approvals necessários
2. CI deve passar
3. Documentação atualizada
4. Cobertura de testes mantida/melhorada

## Setup de Desenvolvimento
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/docsync.git
cd docsync

# Crie e ative ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Instale dependências
pip install -e ".[dev]"

# Instale pre-commit hooks
pre-commit install

# Execute testes
pytest
```

## Recursos Úteis
- [Documentação](https://docsync.readthedocs.io)
- [Issues](https://github.com/seu-usuario/docsync/issues)
- [Pull Requests](https://github.com/seu-usuario/docsync/pulls)
- [Changelog](CHANGELOG.md)

## Dúvidas?
Abra uma issue ou envie um email para dev@example.com


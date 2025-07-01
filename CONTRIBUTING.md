# Contributing to DocSync

First off, thank you for considering contributing to DocSync! 🎉

This document provides guidelines and important information for contributing to the project.

**[🇧🇷 Português](./docs/pt-br/CONTRIBUTING.md) | 🇺🇸 English**

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Pull Requests](#pull-requests)
- [Code Style](#code-style)
- [Commits](#commits)
- [Testing](#testing)
- [Development Setup](#development-setup)
- [Useful Resources](#useful-resources)

## 📜 Code of Conduct

This project follows a Code of Conduct that all contributors must observe. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

1. Check if the bug hasn't already been reported
2. Use the bug issue template
3. Include detailed steps to reproduce
4. Provide environment information (OS, Python version, etc.)
5. Add relevant logs and screenshots

### 💡 Suggesting Enhancements

1. First discuss the enhancement via issue
2. Use the feature request template
3. Describe the problem your suggestion solves
4. Explain how your suggestion benefits the project
5. Include usage examples
6. Consider backward compatibility

## 🔄 Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/MyFeature`)
3. Implement your changes
4. Add or update tests
5. Update documentation
6. Run tests (`pytest`)
7. Commit using clear messages
8. Push to your branch (`git push origin feature/MyFeature`)
9. Open a Pull Request

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (black)
- [ ] Imports sorted (isort)
- [ ] Types checked (mypy)
- [ ] Changelog updated
- [ ] Version incremented if needed
- [ ] 100% coverage on new code

## 💻 Code Style

### Python

- Use Python 3.9+
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Static types with [mypy](http://mypy-lang.org/)
- Google-style docstrings
- Type hints on all functions

```python
def calculate_metric(value: float, target: float) -> float:
    """Calculate percentage difference between value and target.

    Args:
        value: Current metric value
        target: Target metric value

    Returns:
        float: Percentage difference

    Raises:
        ValueError: If target is zero
    """
    if target == 0:
        raise ValueError("Target cannot be zero")
    return (value - target) / target * 100
```

### Imports

We use `isort` with the following configuration:

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
```

## 📝 Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/) standard:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

Example:
```
feat(templates): Add custom theme support

- Implement theme system
- Add documentation
- Include tests
```

## ✅ Testing

- Use `pytest` for testing
- Maintain coverage above 80%
- Include integration tests when necessary
- Use fixtures for repetitive code
- Mock external resources

```python
@pytest.fixture
def doc_sync():
    """Fixture that provides configured DocSync instance."""
    return DocSync(templates_path="tests/fixtures/templates")

def test_generate_report(doc_sync):
    """Test basic report generation."""
    result = doc_sync.generate_report(
        template_name="test",
        data={"title": "Test"}
    )
    assert result.success
```

## 🛠️ Development Setup

```bash
# Clone the repository
git clone https://github.com/NEO-SH1W4/docsync.git
cd docsync

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📦 Dependency Management

- Use `pyproject.toml` for dependencies
- Keep dependencies updated
- Document breaking changes

## 🔍 Review Process

1. Two approvers required
2. CI must pass
3. Documentation updated
4. Test coverage maintained/improved

## 📚 Useful Resources

- [Documentation](https://github.com/NEO-SH1W4/docsync#readme)
- [Issues](https://github.com/NEO-SH1W4/docsync/issues)
- [Pull Requests](https://github.com/NEO-SH1W4/docsync/pulls)
- [Changelog](CHANGELOG.md)

## ❓ Questions?

- Open an issue
- Email us at dev@example.com
- Check the documentation

Thank you for contributing! 🎉


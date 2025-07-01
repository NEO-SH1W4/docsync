import os

from setuptools import find_packages, setup


def read(fname):
    """Lê o conteúdo de um arquivo."""
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


def read_requirements(fname):
    """Lê requisitos de um arquivo, ignorando comentários e linhas vazias."""
    requirements = []
    for line in read(fname).splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-r"):
            requirements.append(line)
    return requirements


setup(
    # Metadados do pacote
    name="docsync",
    version="1.0.0",
    author="GUARDRIVE Team",
    author_email="dev@guardrive.com",
    description="Sistema quântico de sincronização de documentação com Notion",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="notion sync markdown documentation quantum",
    url="https://github.com/guardrive/docsync",
    # Configuração do pacote
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.9",
    # Dependências
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "docs": [
            "mkdocs==1.4.3",
            "mkdocs-material==9.1.18",
            "mkdocstrings==0.22.0",
            "mkdocstrings-python==1.1.2",
        ],
        "test": [
            "pytest==7.4.0",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0",
            "pytest-mock==3.11.1",
            "aioresponses==0.7.4",
        ],
        "lint": [
            "black==23.7.0",
            "isort==5.12.0",
            "flake8==6.0.0",
            "mypy==1.4.1",
        ],
    },
    # Entry points para CLI
    entry_points={
        "console_scripts": [
            "docsync=docsync.cli:main",
            "docsync-monitor=docsync.monitor:main",
        ],
    },
    # Dados do pacote
    package_data={
        "docsync": [
            "templates/*.j2",
            "config/*.yaml",
        ],
    },
    # Classificadores
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Environment :: Console",
        "Natural Language :: Portuguese (Brazilian)",
    ],
    # Informações de projeto
    project_urls={
        "Bug Reports": "https://github.com/guardrive/docsync/issues",
        "Source": "https://github.com/guardrive/docsync",
        "Documentation": "https://docsync.guardrive.dev",
        "Changelog": "https://github.com/guardrive/docsync/blob/main/CHANGELOG.md",
    },
)

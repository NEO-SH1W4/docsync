"""Plugin para suporte a documentos RMarkdown."""

import logging
from pathlib import Path
from typing import Any, Optional

from rich.logging import RichHandler

from docsync.plugins import DocumentFormat, PluginMetadata


class RMarkdownFormat(DocumentFormat):
    """Plugin para processamento de documentos RMarkdown."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rmarkdown",
            version="0.1.0",
            description="Suporte para documentos RMarkdown",
            author="GUARDRIVE Team",
            requires=["rpy2>=3.5.0", "pandas>=1.3.0"],
        )

    def __init__(self) -> None:
        """Inicializa o plugin RMarkdown."""
        self.logger = logging.getLogger("docsync.plugins.rmarkdown")
        self.logger.handlers = [RichHandler()]
        self.logger.setLevel(logging.INFO)
        self.initialized = False

        # Configurações R
        self.r_libs = ["rmarkdown", "knitr", "tidyverse"]

    def initialize(self, config: dict) -> None:
        """Inicializa o plugin verificando dependências.

        Args:
            config: Configuração do plugin
        """
        try:
            from rpy2 import robjects
            from rpy2.robjects.packages import importr

            # Verificar/instalar pacotes R necessários
            utils = importr("utils")
            for lib in self.r_libs:
                if not robjects.r(f"require({lib})")[0]:
                    self.logger.info(f"📦 Instalando pacote R: {lib}")
                    utils.install_packages(lib)

            self.initialized = True
            self.logger.info("✨ Plugin RMarkdown inicializado")

        except ImportError:
            msg = (
                "rpy2 é necessário para o plugin RMarkdown. "
                "Instale com: pip install rpy2"
            )
            raise ImportError(
                msg,
            )

    def cleanup(self) -> None:
        """Limpa recursos do plugin."""

    def can_handle(self, file_path: Path) -> bool:
        """Verifica se arquivo é RMarkdown.

        Args:
            file_path: Caminho do arquivo

        Returns:
            bool: True se for RMarkdown
        """
        return file_path.suffix.lower() in [".rmd", ".rmarkdown"]

    def read_document(self, file_path: Path) -> dict[str, Any]:
        """Lê documento RMarkdown e extrai conteúdo/metadados.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dict[str, Any]: Conteúdo e metadados
        """
        from rpy2 import robjects

        # Extrair YAML frontmatter
        r_code = f"""
        yaml::read_yaml("{file_path!s}")
        """
        metadata = dict(robjects.r(r_code))

        # Ler conteúdo
        content = file_path.read_text(encoding="utf-8")

        return {"metadata": metadata, "content": content}

    def write_document(self, file_path: Path, content: dict[str, Any]) -> None:
        """Escreve documento RMarkdown.

        Args:
            file_path: Caminho do arquivo
            content: Conteúdo e metadados
        """
        from rpy2.robjects.packages import importr

        yaml = importr("yaml")

        # Gerar YAML frontmatter
        frontmatter = yaml.as_yaml(content["metadata"])

        # Combinar com conteúdo
        full_content = f"---\n{frontmatter}\n---\n\n{content['content']}"

        # Salvar arquivo
        file_path.write_text(full_content, encoding="utf-8")

    def render_document(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        format: str = "html",
    ) -> Path:
        """Renderiza documento RMarkdown.

        Args:
            input_path: Arquivo RMarkdown
            output_path: Caminho de saída opcional
            format: Formato de saída (html, pdf, word)

        Returns:
            Path: Caminho do arquivo gerado
        """
        from rpy2 import robjects

        if not output_path:
            output_path = input_path.with_suffix(f".{format}")

        # Código R para renderização
        r_code = f"""
        rmarkdown::render(
            "{input_path!s}",
            output_file = "{output_path!s}",
            output_format = "{format}_document"
        )
        """

        # Renderizar
        self.logger.info(f"🔄 Renderizando {input_path}")
        robjects.r(r_code)
        self.logger.info(f"✨ Documento gerado: {output_path}")

        return output_path

    def get_references(self, file_path: Path) -> list[str]:
        """Extrai referências do documento.

        Args:
            file_path: Caminho do arquivo

        Returns:
            List[str]: Lista de referências
        """
        from rpy2 import robjects

        # Extrair citações e links
        r_code = f"""
        refs <- list()

        # Extrair citações
        citations <- stringr::str_extract_all(
            readLines("{file_path!s}"),
            "@[[:alnum:]_-]+"
        )
        refs$citations <- unlist(citations)

        # Extrair links
        links <- stringr::str_extract_all(
            readLines("{file_path!s}"),
            "\\[([^]]+)\\]\\(([^)]+)\\)"
        )
        refs$links <- unlist(links)

        refs
        """

        refs = robjects.r(r_code)
        return list(refs)

    def update_references(self, file_path: Path, updates: dict[str, str]) -> None:
        """Atualiza referências no documento.

        Args:
            file_path: Caminho do arquivo
            updates: Mapeamento de atualizações
        """
        content = file_path.read_text(encoding="utf-8")

        # Atualizar cada referência
        for old_ref, new_ref in updates.items():
            content = content.replace(old_ref, new_ref)

        file_path.write_text(content, encoding="utf-8")

"""
Exemplo de uso do plugin RMarkdown.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from docsync import DocSync
from docsync.plugins.formats import RMarkdownFormat

console = Console()

def main():
    """Executa exemplo de processamento RMarkdown."""
    try:
        # Inicializar DocSync
        doc_sync = DocSync(".")
        
        # Registrar plugin RMarkdown
        rmd = RMarkdownFormat()
        doc_sync.register_plugin(rmd)
        
        # Arquivo de exemplo
        example = """---
title: "Análise ESG"
author: "GUARDRIVE Team"
date: "2024-01-01"
output: html_document
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(tidyverse)
```

## Métricas ESG

```{r metrics}
metrics <- tribble(
  ~category, ~metric, ~value, ~target,
  "Ambiental", "Emissão CO2", 125.5, 100,
  "Social", "Diversidade", 42, 50,
  "Governança", "Compliance", 98, 100
)

metrics %>%
  ggplot(aes(x = metric, y = value, fill = category)) +
  geom_col() +
  geom_hline(aes(yintercept = target)) +
  facet_wrap(~category, scales = "free") +
  theme_minimal() +
  labs(title = "Métricas ESG vs Metas")
```
"""
        
        # Criar arquivo
        input_path = Path("example.rmd")
        input_path.write_text(example)
        
        # Renderizar documento
        console.print(Panel("🔄 Processando documento RMarkdown"))
        output_path = rmd.render_document(input_path)
        
        console.print(f"\n✨ Documento gerado: {output_path}")
        
    except Exception as e:
        console.print(f"\n❌ Erro: {e}", style="red")
        raise

if __name__ == "__main__":
    main()


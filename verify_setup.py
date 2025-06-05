#!/usr/bin/env python3
"""
Script de verificação do sistema DOCSYNC.

Verifica a instalação, configuração e prontidão do sistema
de sincronização de documentação GUARDRIVE.

Author: DocSync Team
Date: 2025-06-03
"""

import os
import sys
import pkg_resources
import importlib
import platform
import subprocess
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import print as rprint

# Configuração do console rich
console = Console()

class SetupVerifier:
    """Verificador de instalação e configuração do sistema."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_dirs = [
            "templates",
            "docs",
            "src/docsync",
            "tests",
            "backups",
            "logs"
        ]
        self.required_files = [
            "guardrive_sync.yaml",
            "src/docsync/config.py",
            "src/docsync/sync_manager.py",
            "run_sync.py"
        ]
        self.required_packages = [
            "aiofiles",
            "watchdog",
            "PyYAML",
            "gitpython",
            "aiogit",
            "croniter",
            "python-dateutil",
            "rich",
            "pytest"
        ]
        self.template_files = [
            "technical/technical_spec.md",
            "api/api_spec.md",
            "project/project_spec.md",
            "guidelines/development_guidelines.md",
            "integration/integration_spec.md"
        ]
        
    def verify_all(self) -> bool:
        """Executa todas as verificações do sistema."""
        with Progress() as progress:
            task = progress.add_task("[cyan]Verificando sistema...", total=7)
            
            results = []
            
            # 1. Verifica dependências
            progress.update(task, advance=1, description="[cyan]Verificando dependências...")
            results.append(("Dependências", self.check_dependencies()))
            
            # 2. Verifica configuração
            progress.update(task, advance=1, description="[cyan]Verificando configuração...")
            results.append(("Configuração", self.check_configuration()))
            
            # 3. Verifica diretórios
            progress.update(task, advance=1, description="[cyan]Verificando diretórios...")
            results.append(("Diretórios", self.check_directories()))
            
            # 4. Verifica templates
            progress.update(task, advance=1, description="[cyan]Verificando templates...")
            results.append(("Templates", self.check_templates()))
            
            # 5. Verifica Git
            progress.update(task, advance=1, description="[cyan]Verificando Git...")
            results.append(("Git", self.check_git()))
            
            # 6. Verifica logging
            progress.update(task, advance=1, description="[cyan]Verificando logging...")
            results.append(("Logging", self.check_logging()))
            
            # 7. Verifica monitoramento
            progress.update(task, advance=1, description="[cyan]Verificando monitoramento...")
            results.append(("Monitoramento", self.check_monitoring()))
            
        self._print_report(results)
        return all(result[1][0] for result in results)
        
    def check_dependencies(self) -> Tuple[bool, str]:
        """Verifica se todas as dependências estão instaladas."""
        try:
            pkg_resources.require(self.required_packages)
            return True, "Todas as dependências instaladas corretamente"
        except pkg_resources.DistributionNotFound as e:
            return False, f"Dependência faltante: {e}"
        except Exception as e:
            return False, f"Erro ao verificar dependências: {e}"
            
    def check_configuration(self) -> Tuple[bool, str]:
        """Verifica arquivo de configuração."""
        config_path = self.project_root / "guardrive_sync.yaml"
        try:
            if not config_path.exists():
                return False, "Arquivo de configuração não encontrado"
                
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            required_keys = ["guardrive", "sync", "templates_dir"]
            if not all(key in config for key in required_keys):
                return False, "Configuração incompleta"
                
            return True, "Configuração válida"
        except Exception as e:
            return False, f"Erro ao verificar configuração: {e}"
            
    def check_directories(self) -> Tuple[bool, str]:
        """Verifica estrutura de diretórios e permissões."""
        try:
            missing_dirs = []
            for dir_name in self.required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
                elif not os.access(dir_path, os.R_OK | os.W_OK):
                    return False, f"Permissões insuficientes para: {dir_name}"
                    
            if missing_dirs:
                return False, f"Diretórios faltantes: {', '.join(missing_dirs)}"
                
            return True, "Estrutura de diretórios correta"
        except Exception as e:
            return False, f"Erro ao verificar diretórios: {e}"
            
    def check_templates(self) -> Tuple[bool, str]:
        """Verifica templates de documentação."""
        try:
            templates_dir = self.project_root / "templates"
            missing_templates = []
            
            for template in self.template_files:
                template_path = templates_dir / template
                if not template_path.exists():
                    missing_templates.append(template)
                    
            if missing_templates:
                return False, f"Templates faltantes: {', '.join(missing_templates)}"
                
            return True, "Todos os templates disponíveis"
        except Exception as e:
            return False, f"Erro ao verificar templates: {e}"
            
    def check_git(self) -> Tuple[bool, str]:
        """Verifica integração com Git."""
        try:
            # Verifica Git instalado
            subprocess.run(["git", "--version"], 
                         check=True, 
                         capture_output=True)
            
            # Verifica repositório
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                return False, "Repositório Git não inicializado"
                
            return True, "Integração Git funcional"
        except subprocess.CalledProcessError:
            return False, "Git não encontrado no sistema"
        except Exception as e:
            return False, f"Erro ao verificar Git: {e}"
            
    def check_logging(self) -> Tuple[bool, str]:
        """Verifica configuração de logging."""
        try:
            log_dir = self.project_root / "logs"
            if not log_dir.exists():
                return False, "Diretório de logs não encontrado"
                
            # Testa escrita de log
            test_logger = logging.getLogger("test")
            test_logger.setLevel(logging.INFO)
            test_file = log_dir / "test.log"
            handler = logging.FileHandler(test_file)
            test_logger.addHandler(handler)
            test_logger.info("Test log entry")
            handler.close()
            
            if not test_file.exists():
                return False, "Não foi possível escrever logs"
                
            test_file.unlink()  # Remove arquivo de teste
            return True, "Sistema de logging funcional"
        except Exception as e:
            return False, f"Erro ao verificar logging: {e}"
            
    def check_monitoring(self) -> Tuple[bool, str]:
        """Verifica capacidades de monitoramento."""
        try:
            # Verifica watchdog
            if not importlib.util.find_spec("watchdog"):
                return False, "Watchdog não instalado"
                
            # Verifica prometheus_client
            if not importlib.util.find_spec("prometheus_client"):
                return False, "Prometheus client não instalado"
                
            return True, "Sistema de monitoramento funcional"
        except Exception as e:
            return False, f"Erro ao verificar monitoramento: {e}"
            
    def _print_report(self, results: List[Tuple[str, Tuple[bool, str]]]):
        """Imprime relatório de verificação."""
        table = Table(title="Relatório de Verificação do Sistema")
        
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="cyan")
        table.add_column("Detalhes", style="cyan")
        
        for component, (status, message) in results:
            status_str = "[green]✓" if status else "[red]✗"
            table.add_row(component, status_str, message)
            
        console.print("\n")
        console.print(table)
        console.print("\n")
        
        if all(result[1][0] for result in results):
            rprint("[green]Sistema verificado e pronto para uso!")
        else:
            rprint("[red]Sistema requer atenção. Corrija os problemas indicados acima.")

def main():
    """Função principal de execução."""
    try:
        verifier = SetupVerifier()
        if not verifier.verify_all():
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Verificação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Erro fatal durante verificação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


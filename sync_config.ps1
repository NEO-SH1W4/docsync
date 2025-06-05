#!/usr/bin/env pwsh

# Configuração de diretórios base
$GUARDRIVE_ROOT = "C:\Users\João\Desktop\PROJETOS\GUARDRIVE\GUARDRIVE_V1"
$DOCS_DEV_ROOT = Join-Path $GUARDRIVE_ROOT "1. GUARDRIVE_DOCS_DEV"
$GUARDRIVE_DOCS = Join-Path $DOCS_DEV_ROOT "GUARDRIVE_DOCS"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

# Configurações específicas para cada diretório
$DIRECTORY_CONFIGS = @{
    "01_TECHNICAL" = @{
        Description = "Configuração DOCSYNC para documentação Técnica do GUARDRIVE"
        SourcePath = "2.AREA_DEV/01_TECHNICAL"
        TargetPath = "GUARDRIVE_DOCS/01_TECHNICAL"
        FilePatterns = @("*.md", "*.yaml", "*.json", "*.drawio", "*.puml", "*.swagger", "*.openapi", "*.proto")
        DirPattern = "^[a-z]+(_[a-z]+)*$"
        Mappings = @{
            "api" = @{
                Source = "api/"
                Target = "../*/api/"
                SyncMode = "two_way"
                Validate = "swagger"
            }
            "architecture" = @{
                Source = "architecture/"
                Target = "../*/architecture/"
                SyncMode = "two_way"
                Validate = "diagrams"
            }
        }
        SpecialConfig = @{
            api_version = "v1"
            openapi_version = "3.0.0"
            supported_protocols = @("REST", "GraphQL", "gRPC")
        }
    }
    "02_BUSINESS" = @{
        Description = "Configuração DOCSYNC para documentação de Negócios do GUARDRIVE"
        SourcePath = "2.AREA_DEV/02_BUSINESS"
        TargetPath = "GUARDRIVE_DOCS/02_BUSINESS"
        FilePatterns = @("*.md", "*.xlsx", "*.pptx", "*.pdf", "*.docx", "*.canvas", "*.bmpr")
        DirPattern = "^[a-z]+(_[a-z]+)*$"
        Mappings = @{
            "market_analysis" = @{
                Source = "market_analysis/"
                Target = "../*/market_analysis/"
                SyncMode = "two_way"
                Validate = "business_data"
            }
            "financial" = @{
                Source = "financial/"
                Target = "../*/financial/"
                SyncMode = "restricted"
                Validate = "sensitive"
            }
        }
        SpecialConfig = @{
            confidentiality_level = "high"
            review_required = $true
            stakeholder_approval = $true
        }
    }
    "03_PRODUCT" = @{
        Description = "Configuração DOCSYNC para documentação de Produto do GUARDRIVE"
        SourcePath = "2.AREA_DEV/03_PRODUCT"
        TargetPath = "GUARDRIVE_DOCS/03_PRODUCT"
        FilePatterns = @("*.md", "*.sketch", "*.fig", "*.xd", "*.png", "*.ai")
        DirPattern = "^[a-z]+(_[a-z]+)*$"
        Mappings = @{
            "ui_design" = @{
                Source = "ui_design/"
                Target = "../*/ui_design/"
                SyncMode = "two_way"
                Validate = "design"
            }
            "prototypes" = @{
                Source = "prototypes/"
                Target = "../*/prototypes/"
                SyncMode = "two_way"
                Validate = "interactive"
            }
        }
        SpecialConfig = @{
            design_system = "guardrive_design_system"
            prototype_tool = "figma"
            version_control = $true
        }
    }
    "04_ASSETS" = @{
        Description = "Configuração DOCSYNC para Assets do GUARDRIVE"
        SourcePath = "2.AREA_DEV/04_ASSETS"
        TargetPath = "GUARDRIVE_DOCS/04_ASSETS"
        FilePatterns = @("*.svg", "*.png", "*.jpg", "*.gif", "*.mp4", "*.webp")
        DirPattern = "^[a-z]+(_[a-z]+)*$"
        Mappings = @{
            "images" = @{
                Source = "images/"
                Target = "../*/images/"
                SyncMode = "two_way"
                Validate = "image"
            }
            "videos" = @{
                Source = "videos/"
                Target = "../*/videos/"
                SyncMode = "two_way"
                Validate = "video"
            }
        }
        SpecialConfig = @{
            compression = "enabled"
            max_file_size = "50MB"
            allowed_formats = @("svg", "png", "jpg", "webp")
        }
    }
}

# Função para criar backup de arquivo existente
function Backup-ExistingConfig {
    param (
        [string]$FilePath
    )
    
    if (Test-Path $FilePath) {
        $BackupPath = "${FilePath}.backup_${TIMESTAMP}"
        Copy-Item -Path $FilePath -Destination $BackupPath
        Write-Host "Backup criado: $BackupPath"
        return $true
    }
    return $false
}

# Função para gerar o conteúdo do YAML
function Get-DocSyncYamlContent {
    param (
        [string]$DirName,
        [hashtable]$Config
    )
    
    $YamlContent = @"
# DOCSYNC Configuration for $($DirName) Documentation
version: '1.0'
meta:
  description: "$($Config.Description)"
  last_updated: "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"

sync:
  paths:
    source: "$($Config.SourcePath)"
    target: "$($Config.TargetPath)"
    
  patterns:
    include:
$(($Config.FilePatterns | ForEach-Object { "      - `"$_`"" }) -join "`n")
    
    directory_naming:
      pattern: "$($Config.DirPattern)"

directory_mappings:
$(($Config.Mappings.GetEnumerator() | ForEach-Object {
    @"
  $($_.Key):
    source: "$($_.Value.Source)"
    target: "$($_.Value.Target)"
    sync_mode: "$($_.Value.SyncMode)"
    validate: "$($_.Value.Validate)"
"@
}) -join "`n")

special_config:
$(($Config.SpecialConfig.GetEnumerator() | ForEach-Object {
    if ($_.Value -is [array]) {
        @"
  $($_.Key):
$(($_.Value | ForEach-Object { "    - `"$_`"" }) -join "`n")
"@
    } else {
        "  $($_.Key): $($_.Value)"
    }
}) -join "`n")

validation:
  enabled: true
  frequency: "on_change"
  notify_on_failure: true
"@

    return $YamlContent
}

# Função principal para sincronizar configurações
function Sync-DocSyncConfigs {
    foreach ($DirName in $DIRECTORY_CONFIGS.Keys) {
        $TargetDir = Join-Path $GUARDRIVE_DOCS $DirName
        $ConfigFile = Join-Path $TargetDir "docsync.yaml"
        
        # Criar diretório se não existir
        if (-not (Test-Path $TargetDir)) {
            New-Item -ItemType Directory -Path $TargetDir -Force
            Write-Host "Diretório criado: $TargetDir"
        }
        
        # Backup da configuração existente
        Backup-ExistingConfig -FilePath $ConfigFile
        
        # Gerar e salvar nova configuração
        $YamlContent = Get-DocSyncYamlContent -DirName $DirName -Config $DIRECTORY_CONFIGS[$DirName]
        $YamlContent | Out-File -FilePath $ConfigFile -Encoding UTF8 -Force
        
        Write-Host "Configuração atualizada: $ConfigFile"
    }
}

# Executar sincronização
try {
    Write-Host "Iniciando sincronização de configurações DOCSYNC..."
    Sync-DocSyncConfigs
    Write-Host "Sincronização concluída com sucesso!"
} catch {
    Write-Error "Erro durante a sincronização: $_"
    exit 1
}


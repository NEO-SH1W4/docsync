# DOCSYNC Quality Fix Script
# Automated script for applying Ruff fixes by priority level

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("critical", "high", "medium", "low", "all", "baseline")]
    [string]$Priority,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$Stats
)

Write-Host "DOCSYNC Quality Fix Tool v1.0" -ForegroundColor Blue
Write-Host "Following VIREON Quality Standards" -ForegroundColor Gray

# Get current stats
function Get-RuffStats {
    $output = ruff check . --statistics 2>&1
    if ($LASTEXITCODE -eq 0) {
        $lines = $output -split "`n"
        $summary = $lines | Where-Object { $_ -match "Found (\d+) error" }
        if ($summary) {
            $count = [regex]::Match($summary, "(\d+)").Groups[1].Value
            return [int]$count
        }
    }
    return 0
}

# Generate baseline if requested
if ($Priority -eq "baseline") {
    Write-Host "${Yellow}📊 Generating quality baseline...${Reset}"
    ruff check . --statistics > "quality_baseline_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    $current = Get-RuffStats
    Write-Host "${Green}✓ Baseline created: $current issues found${Reset}"
    exit 0
}

# Show stats if requested
if ($Stats) {
    Write-Host "${Blue}📈 Current Quality Statistics:${Reset}"
    ruff check . --statistics
    exit 0
}

# Get initial count
$initialCount = Get-RuffStats
Write-Host "${Blue}Starting with: $initialCount issues${Reset}"

# Define rule sets by priority
$ruleSets = @{
    "critical" = @{
        "rules" = "BLE001,UP035,DTZ005,TRY400,PTH123"
        "description" = "Type Safety & Runtime Errors"
        "target" = 800
    }
    "high" = @{
        "rules" = "ANN,D205,D415,G004,TRY003"
        "description" = "Code Quality & Maintainability" 
        "target" = 600
    }
    "medium" = @{
        "rules" = "F841,ARG,PLC0415,SIM117,E501,W293"
        "description" = "Best Practices & Style"
        "target" = 400
    }
    "low" = @{
        "rules" = "PT,S106,ERA001,INP001"
        "description" = "Minor Style & Conventions"
        "target" = 200
    }
}

# Execute fixes
if ($Priority -eq "all") {
    Write-Host "${Yellow}🚀 Running ALL priority fixes...${Reset}"
    
    foreach ($level in @("critical", "high", "medium", "low")) {
        $ruleSet = $ruleSets[$level]
        Write-Host "`n${Blue}Phase: $level - $($ruleSet.description)${Reset}"
        
        if ($DryRun) {
            Write-Host "${Yellow}[DRY RUN] Would execute: ruff check . --select=$($ruleSet.rules) --fix --unsafe-fixes${Reset}"
        } else {
            ruff check . --select=$ruleSet.rules --fix --unsafe-fixes
            $currentCount = Get-RuffStats
            Write-Host "${Green}✓ Phase completed. Current: $currentCount issues${Reset}"
        }
    }
} else {
    $ruleSet = $ruleSets[$Priority]
    Write-Host "`n${Blue}🎯 Applying $Priority priority fixes${Reset}"
    Write-Host "Category: $($ruleSet.description)"
    Write-Host "Rules: $($ruleSet.rules)"
    Write-Host "Target: $($ruleSet.target) issues"
    
    if ($DryRun) {
        Write-Host "${Yellow}[DRY RUN] Would execute: ruff check . --select=$($ruleSet.rules) --fix --unsafe-fixes${Reset}"
    } else {
        ruff check . --select=$ruleSet.rules --fix --unsafe-fixes
    }
}

# Show final results
if (-not $DryRun) {
    $finalCount = Get-RuffStats
    $fixed = $initialCount - $finalCount
    
    Write-Host "`n${Green}🎉 Quality Fix Complete!${Reset}"
    Write-Host "Issues fixed: ${Green}$fixed${Reset}"
    Write-Host "Remaining: ${Yellow}$finalCount${Reset}"
    
    if ($Priority -ne "all") {
        $target = $ruleSets[$Priority].target
        $progress = [math]::Round((($initialCount - $finalCount) / ($initialCount - $target)) * 100, 1)
        Write-Host "Progress to target: ${Blue}$progress%${Reset}"
    }
    
    # Suggest next steps
    Write-Host "`n${Blue}💡 Next Steps:${Reset}"
    if ($finalCount -gt 800) {
        Write-Host "• Run: .\quality_fix.ps1 critical"
    } elseif ($finalCount -gt 600) {
        Write-Host "• Run: .\quality_fix.ps1 high"
    } elseif ($finalCount -gt 400) {
        Write-Host "• Run: .\quality_fix.ps1 medium"
    } elseif ($finalCount -gt 200) {
        Write-Host "• Run: .\quality_fix.ps1 low"
    } else {
        Write-Host "• ${Green}Congratulations! Target achieved 🎯${Reset}"
        Write-Host "• Consider setting up pre-commit hooks"
        Write-Host "• Review QUALITY_ROADMAP.md for next phase"
    }
}

Write-Host "`n${Blue}For help: .\quality_fix.ps1 -Priority baseline -Stats${Reset}"


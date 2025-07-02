# DOCSYNC Quality Fix Script - Simplified Version
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("critical", "high", "medium", "low", "all", "stats")]
    [string]$Priority
)

Write-Host "DOCSYNC Quality Fix Tool v1.0" -ForegroundColor Blue

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

# Show stats if requested
if ($Priority -eq "stats") {
    Write-Host "Current Quality Statistics:" -ForegroundColor Cyan
    ruff check . --statistics
    exit 0
}

# Define rule sets by priority
$ruleSets = @{
    "critical" = "BLE001,UP035,DTZ005,TRY400,PTH123"
    "high" = "ANN,D205,D415,G004,TRY003"
    "medium" = "F841,ARG,PLC0415,SIM117,E501,W293"
    "low" = "PT,S106,ERA001,INP001"
}

# Get initial count
$initialCount = Get-RuffStats
Write-Host "Starting with: $initialCount issues" -ForegroundColor Yellow

# Execute fixes
if ($Priority -eq "all") {
    Write-Host "Running ALL priority fixes..." -ForegroundColor Green
    
    foreach ($level in @("critical", "high", "medium", "low")) {
        $rules = $ruleSets[$level]
        Write-Host "Phase: $level" -ForegroundColor Cyan
        ruff check . --select=$rules --fix --unsafe-fixes
        $currentCount = Get-RuffStats
        Write-Host "Current: $currentCount issues" -ForegroundColor Yellow
    }
} else {
    $rules = $ruleSets[$Priority]
    Write-Host "Applying $Priority priority fixes" -ForegroundColor Cyan
    Write-Host "Rules: $rules"
    ruff check . --select=$rules --fix --unsafe-fixes
}

# Show final results
$finalCount = Get-RuffStats
$fixed = $initialCount - $finalCount

Write-Host ""
Write-Host "Quality Fix Complete!" -ForegroundColor Green
Write-Host "Issues fixed: $fixed" -ForegroundColor Green
Write-Host "Remaining: $finalCount" -ForegroundColor Yellow

# Suggest next steps
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Blue
if ($finalCount -gt 800) {
    Write-Host "Run: .\quality_fix_simple.ps1 critical"
} elseif ($finalCount -gt 600) {
    Write-Host "Run: .\quality_fix_simple.ps1 high"
} elseif ($finalCount -gt 400) {
    Write-Host "Run: .\quality_fix_simple.ps1 medium"
} elseif ($finalCount -gt 200) {
    Write-Host "Run: .\quality_fix_simple.ps1 low"
} else {
    Write-Host "Congratulations! Target achieved!" -ForegroundColor Green
}


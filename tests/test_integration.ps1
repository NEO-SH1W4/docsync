# Test script for DOCSYNC AI integration
Write-Host "=== Testing DOCSYNC AI Integration ==="

# Verify Python environment
Write-Host "
Checking Python environment..."
python -c "import yaml, watchdog" 2>&1

# Check test directory
Write-Host "
Setting up test directory..."
$testDir = "C:\Users\João\Desktop\PROJETOS\DOCSYNC\tests\test_docs"
New-Item -ItemType Directory -Force -Path $testDir | Out-Null

# Create test files
@'
---
title: Test Document
date: 2024-03-14
---
# Test Header
This is a test document.
`python
print("Hello World")
`
'@ | Out-File -Path "$testDir\test.md" -Encoding UTF8

@'
config:
  monitoring:
    enabled: true
    patterns: [".md", ".yaml"]
  processing:
    cache_ttl: 3600
'@ | Out-File -Path "$testDir\config.yaml" -Encoding UTF8

Write-Host "
Test files created in: $testDir"
Write-Host "Run integration tests with: python -m pytest tests/"

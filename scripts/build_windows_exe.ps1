[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$specPath = Join-Path $projectRoot 'UniversalInvoiceMail.spec'
$readinessScript = Join-Path $PSScriptRoot 'check_store_readiness.py'

Push-Location $projectRoot
try {
    & python -m PyInstaller --clean --noconfirm $specPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }

    & python $readinessScript --project-root $projectRoot --require-exe
    if ($LASTEXITCODE -ne 0) {
        throw "Store artifact check failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

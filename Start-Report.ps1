param([switch]$UseAI, [switch]$NoOpen)
$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    $uvPath = if ($uvCommand) { $uvCommand.Source } else {
        Join-Path $PSScriptRoot '.tools/bootstrap/bin/uv.exe'
    }
    if (-not (Test-Path -LiteralPath $uvPath)) {
        throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
    }
    $env:UV_CACHE_DIR = Join-Path $PSScriptRoot '.tools/p1-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $PSScriptRoot '.tools/python'
    $env:UV_LINK_MODE = 'copy'
    & $uvPath sync --locked
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & $uvPath run adsreport doctor
    if ($LASTEXITCODE -ne 0) {
        throw 'Complete local setup first. Windows PDF setup: uv run python scripts/setup_windows_pdf.py'
    }
    $reportArgs = @('run', 'adsreport', 'run')
    if (-not $UseAI) { $reportArgs += '--no-ai' }
    if (-not $NoOpen) { $reportArgs += '--open' }
    & $uvPath @reportArgs
    if ($LASTEXITCODE -ne 0) { throw 'Report failed. Inspect runs/run-log.jsonl.' }
} finally {
    Pop-Location
}

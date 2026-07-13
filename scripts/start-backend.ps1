$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"

Set-Location $Backend
& "$Backend\.venv\Scripts\Activate.ps1"
Write-Host "Starting backend on http://127.0.0.1:8005"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8005

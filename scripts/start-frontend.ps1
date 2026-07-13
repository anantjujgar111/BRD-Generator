$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Set-Location $Backend
& "$Backend\.venv\Scripts\Activate.ps1"
$env:BRD_API_BASE = "http://127.0.0.1:8005"
Set-Location $Frontend
Write-Host "Starting Streamlit on http://127.0.0.1:8503"
streamlit run app.py --server.address 127.0.0.1 --server.port 8503

# Magnetar Agentic EXE Builder - Local Development Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Magnetar Labs — Agentic Windows EXE Builder Launcher" -ForegroundColor Header
Write-Host " Engine: Qwen2.5-Coder 32B via Ollama & PyInstaller In-Code" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start FastAPI Backend in background job
Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location "$path\backend"
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $scriptPath

# Start Vite Frontend
Write-Host "[2/2] Starting React Vite Frontend on http://localhost:3000..." -ForegroundColor Green
Set-Location "$scriptPath\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

npm run dev

# Cleanup when frontend stops
Stop-Job $backendJob
Remove-Job $backendJob

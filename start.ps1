$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$PythonExe = Join-Path $Backend ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Backend virtual environment not found. Run .\setup.ps1 first."
}

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    throw "Frontend dependencies not found. Run .\setup.ps1 first."
}

if (-not (Test-Path (Join-Path $Frontend ".env.local"))) {
    Set-Content -LiteralPath (Join-Path $Frontend ".env.local") -Value "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" -Encoding UTF8
}

Write-Host ""
Write-Host "Starting ShadowAI Guardian..." -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow

$BackendCommand = "Set-Location `"$Backend`"; `"$PythonExe`" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
$FrontendCommand = "Set-Location `"$Frontend`"; npm run dev -- -p 3000"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCommand
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCommand
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "App launched. Keep the backend and frontend terminal windows open." -ForegroundColor Green

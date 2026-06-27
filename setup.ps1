$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "ShadowAI Guardian local setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Venv = Join-Path $Backend ".venv"
$PythonExe = Join-Path $Venv "Scripts\python.exe"
$PipExe = Join-Path $Venv "Scripts\pip.exe"

function Get-PythonCommand {
    $commands = @("py -3.12", "py -3.11", "python")
    foreach ($cmd in $commands) {
        try {
            $parts = $cmd.Split(" ")
            $exe = $parts[0]
            $args = $parts[1..($parts.Length - 1)]
            if ($parts.Length -eq 1) { $args = @("--version") } else { $args += "--version" }
            & $exe @args *> $null
            if ($LASTEXITCODE -eq 0) { return $cmd }
        } catch {}
    }
    throw "Python 3.11+ was not found. Install Python from https://www.python.org/downloads/ and rerun setup."
}

function Invoke-Python {
    param([string[]] $Arguments)
    $cmd = Get-PythonCommand
    $parts = $cmd.Split(" ")
    $exe = $parts[0]
    $baseArgs = @()
    if ($parts.Length -gt 1) { $baseArgs = $parts[1..($parts.Length - 1)] }
    & $exe @baseArgs @Arguments
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm was not found. Install Node.js 18+ from https://nodejs.org/ and rerun setup."
}

Write-Host "Creating backend virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path $PythonExe)) {
    Invoke-Python @("-m", "venv", $Venv)
}

Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& $PythonExe -m pip install --upgrade pip
& $PipExe install -r (Join-Path $Backend "requirements.txt")

Write-Host "Creating backend .env..." -ForegroundColor Yellow
$BackendEnv = Join-Path $Backend ".env"
if (-not (Test-Path $BackendEnv)) {
    Copy-Item (Join-Path $Root ".env.example") $BackendEnv
}

Write-Host "Training local ML model..." -ForegroundColor Yellow
Push-Location $Backend
& $PythonExe -m app.ml.train_model
Pop-Location

Write-Host "Creating frontend .env.local..." -ForegroundColor Yellow
Set-Content -LiteralPath (Join-Path $Frontend ".env.local") -Value "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" -Encoding UTF8

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $Frontend
npm install
Pop-Location

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Run the app with: .\start.ps1" -ForegroundColor Green

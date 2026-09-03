# ─────────────────────────────────────────────────────────────────────────────
# setup.ps1 — one-shot project setup for Windows PowerShell
#
#   .\setup.ps1
#
# Creates a virtualenv, installs Python + Node deps, copies .env files.
# Safe to run multiple times (idempotent).
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

function Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }

# ── 1. Python venv ──────────────────────────────────────────────────────────
if (-not (Test-Path ".venv")) {
    Info "Creating Python virtual environment..."
    python -m venv .venv
} else {
    Warn ".venv already exists, skipping creation."
}

# Activate
& ".venv\Scripts\Activate.ps1"

# ── 2. Python dependencies ──────────────────────────────────────────────────
Info "Installing Python dependencies..."
python -m pip install --upgrade pip -q
pip install -r requirements-dev.txt -q
pip install -e . -q

# ── 3. .env files ──────────────────────────────────────────────────────────
$envFiles = @(
    @{ Src = "backend\.env.example"; Dst = "backend\.env" },
    @{ Src = "frontend\.env.example"; Dst = "frontend\.env" }
)
foreach ($pair in $envFiles) {
    if (-not (Test-Path $pair.Dst)) {
        Copy-Item $pair.Src $pair.Dst
        Info "Created $($pair.Dst)"
    } else {
        Warn "$($pair.Dst) already exists, skipping."
    }
}

# ── 4. Frontend dependencies ───────────────────────────────────────────────
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Info "Installing frontend dependencies..."
    Push-Location frontend
    npm install --silent
    Pop-Location
} else {
    Warn "npm not found — skipping frontend install. Install Node.js 18+ first."
}

# ── Done ────────────────────────────────────────────────────────────────────
Write-Host ""
Info "Setup complete. Activate the venv and start developing:"
Write-Host ""
Write-Host "  .venv\Scripts\Activate.ps1"
Write-Host "  make dev          # start backend + frontend"
Write-Host "  make test         # run all tests"
Write-Host "  make help         # see all targets"
Write-Host ""
Info "Or use Docker:"
Write-Host ""
Write-Host "  docker compose up --build"
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# dev.ps1 — Start backend + frontend dev servers on Windows
#
#   .\dev.ps1
#
# Both servers run in separate windows. Close them with Ctrl+C or close the
# windows. The frontend blocks the terminal; the backend runs in the background.
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting backend on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "Starting frontend on http://localhost:5173 ..." -ForegroundColor Green
Write-Host ""

# Start backend in a separate process window so it doesn't block the frontend.
$backendDir = Join-Path $RepoRoot "backend"
Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoExit",
    "-Command", "Set-Location '$backendDir'; python -m uvicorn app.main:app --reload"
) -WindowStyle Normal

# Start frontend in the current window (it blocks with HMR output).
$frontendDir = Join-Path $RepoRoot "frontend"
Set-Location $frontendDir
npm run dev

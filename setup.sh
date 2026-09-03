#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# setup.sh — one-shot project setup for Linux / macOS / Git Bash
#
#   chmod +x setup.sh && ./setup.sh
#
# Creates a virtualenv, installs Python + Node deps, copies .env files.
# Safe to run multiple times (idempotent).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { printf "${GREEN}[INFO]${NC}  %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }

# ── 1. Python venv ──────────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv .venv
else
    warn ".venv already exists, skipping creation."
fi

# shellcheck source=/dev/null
source .venv/bin/activate

# ── 2. Python dependencies ──────────────────────────────────────────────────
info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements-dev.txt -q
pip install -e . -q

# ── 3. .env files ──────────────────────────────────────────────────────────
for pair in "backend/.env.example:backend/.env" "frontend/.env.example:frontend/.env"; do
    src="${pair%%:*}"
    dst="${pair##*:}"
    if [ ! -f "$dst" ]; then
        cp "$src" "$dst"
        info "Created $dst"
    else
        warn "$dst already exists, skipping."
    fi
done

# ── 4. Frontend dependencies ───────────────────────────────────────────────
if command -v npm &>/dev/null; then
    info "Installing frontend dependencies..."
    (cd frontend && npm install --silent)
else
    warn "npm not found — skipping frontend install. Install Node.js 18+ first."
fi

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
info "Setup complete. Activate the venv and start developing:"
echo ""
echo "  source .venv/bin/activate"
echo "  make dev          # start backend + frontend"
echo "  make test         # run all tests"
echo "  make help         # see all targets"
echo ""
info "Or use Docker:"
echo ""
echo "  docker compose up --build"
echo ""

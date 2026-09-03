.PHONY: setup dev backend frontend test clean download-data help docker-build docker-run docker-up

# ─── Platform detection ─────────────────────────────────────────────────────
ifeq ($(OS),Windows_NT)
    # Windows: use PowerShell for shell commands
    SHELL := powershell
    CP    := Copy-Item
    RM    := Remove-Item -Recurse -Force
    MKDIR := New-Item -ItemType Directory -Force -Path
    _Q    := 2>$null; $$null
else
    # Linux / macOS
    CP    := cp -n
    RM    := rm -rf
    MKDIR := mkdir -p
    _Q    := 2>/dev/null || true
endif

# ─── Defaults ────────────────────────────────────────────────────────────────
PYTHON   ?= python
PIP      ?= $(PYTHON) -m pip
NODE     ?= node
NPM      ?= npm

# ─── Help ────────────────────────────────────────────────────────────────────
help: ## Show this help
ifeq ($(OS),Windows_NT)
	@powershell -Command "Write-Host '' -ForegroundColor Cyan; Get-Content $(MAKEFILE_LIST) | Select-String '^[a-zA-Z_-]+:.*?## ' | ForEach-Object { $$line = $$_ -replace '## .*$$',''; $$desc = $$_ -replace '.*## ',''; $$name = ($$line -split ':')[0]; Write-Host ('  {0,-24}' -f $$name) -ForegroundColor Cyan -NoNewline; Write-Host $$desc }"
else
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'
endif

# ─── Setup ───────────────────────────────────────────────────────────────────
setup: ## Full setup: venv + deps + editable install + frontend
	$(PYTHON) -m venv .venv
	@echo ""
	@echo "  Activate your venv first:"
	@echo "    Linux / macOS :  source .venv/bin/activate"
	@echo "    Windows (PS)  :  .venv\Scripts\Activate.ps1"
	@echo "    Windows (cmd) :  .venv\Scripts\activate.bat"
	@echo ""
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	cd frontend && $(NPM) install
ifeq ($(OS),Windows_NT)
	@cmd /c "if not exist backend\.env copy backend\.env.example backend\.env"
	@cmd /c "if not exist frontend\.env copy frontend\.env.example frontend\.env"
else
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@cp -n frontend/.env.example frontend/.env 2>/dev/null || true
endif
	@echo ""
	@echo "Done. Activate your venv, then run 'make dev'."

# ─── Development ─────────────────────────────────────────────────────────────
dev: ## Start backend and frontend dev servers (Ctrl+C to stop)
ifeq ($(OS),Windows_NT)
	powershell -ExecutionPolicy Bypass -File dev.ps1
else
	@echo "Starting backend on http://localhost:8000 ..."
	@echo "Starting frontend on http://localhost:5173 ..."
	@echo ""
	cd backend && ($(PYTHON) -m uvicorn app.main:app --reload &); \
	cd frontend && $(NPM) run dev
endif

backend: ## Start the FastAPI backend only (port 8000)
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload

frontend: ## Start the Vite frontend dev server only (port 5173)
	cd frontend && $(NPM) run dev

notebook: ## Open Jupyter Lab with the training notebook
	$(PYTHON) -m jupyter lab notebooks/house_price_model.ipynb

# ─── Dataset ─────────────────────────────────────────────────────────────────
download-data: ## Download the Kaggle dataset into notebooks/data/
ifeq ($(OS),Windows_NT)
	@New-Item -ItemType Directory -Force -Path notebooks\data
else
	mkdir -p notebooks/data
endif
	@echo "Downloading from Kaggle..."
	$(PYTHON) -c "import urllib.request, zipfile, io; z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen('https://www.kaggle.com/api/v1/datasets/download/juhibhojani/house-price').read())); z.extractall('notebooks/data'); print('Extracted to notebooks/data/')"

# ─── Testing ─────────────────────────────────────────────────────────────────
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend pytest suite
	cd backend && $(PYTHON) -m pytest -v

test-frontend: ## Type-check and build the frontend
	cd frontend && $(NPM) run build

# ─── Docker ──────────────────────────────────────────────────────────────────
docker-build: ## Build the Docker image
	docker build -f backend/Dockerfile -t house-price-api .

docker-run: ## Run the Docker image
	docker run -p 8000:8000 --env-file backend/.env house-price-api

docker-up: ## Start with docker compose
	docker compose up --build

# ─── Cleanup ─────────────────────────────────────────────────────────────────
clean: ## Remove build artifacts
ifeq ($(OS),Windows_NT)
	@powershell -Command "if (Test-Path .venv) { Remove-Item .venv -Recurse -Force }; if (Test-Path __pycache__) { Remove-Item __pycache__ -Recurse -Force }; if (Test-Path '*.egg-info') { Get-ChildItem -Directory *.egg-info | Remove-Item -Recurse -Force }; if (Test-Path build) { Remove-Item build -Recurse -Force }; if (Test-Path dist) { Remove-Item dist -Recurse -Force }; if (Test-Path backend\__pycache__) { Remove-Item backend\__pycache__ -Recurse -Force }; if (Test-Path backend\.pytest_cache) { Remove-Item backend\.pytest_cache -Recurse -Force }; if (Test-Path frontend\node_modules) { Remove-Item frontend\node_modules -Recurse -Force }; if (Test-Path frontend\dist) { Remove-Item frontend\dist -Recurse -Force }; Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
else
	rm -rf .venv __pycache__ *.egg-info build dist
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
endif

.PHONY: setup dev backend frontend test clean download-data help docker-build docker-run

# ─── Defaults ────────────────────────────────────────────────────────────────
PYTHON   ?= python
PIP      ?= $(PYTHON) -m pip
NODE     ?= node
NPM      ?= npm
JUPYTER  ?= $(PYTHON) -m jupyter lab

HELP_WIDTH = 24

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-$(HELP_WIDTH)s\033[0m %s\n", $$1, $$2}'

# ─── Setup ───────────────────────────────────────────────────────────────────
setup: ## Full setup: venv + deps + editable install + frontend
	$(PYTHON) -m venv .venv
	@echo ""
	@echo "  Activate your venv first:"
	@echo "    Linux / macOS :  source .venv/bin/activate"
	@echo "    Windows (PS)  :  .venv\\Scripts\\Activate.ps1"
	@echo "    Windows (cmd) :  .venv\\Scripts\\activate.bat"
	@echo ""
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	cd frontend && $(NPM) install
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@cp -n frontend/.env.example frontend/.env 2>/dev/null || true
	@echo ""
	@echo "Done. Activate your venv, then run 'make dev'."

# ─── Development ─────────────────────────────────────────────────────────────
dev: ## Start backend and frontend dev servers (foreground, Ctrl+C to stop)
	@echo "Starting backend on http://localhost:8000 ..."
	@echo "Starting frontend on http://localhost:5173 ..."
	@echo ""
	cd backend && ($(PYTHON) -m uvicorn app.main:app --reload &); \
	cd frontend && $(NPM) run dev

backend: ## Start the FastAPI backend only (port 8000)
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload

frontend: ## Start the Vite frontend dev server only (port 5173)
	cd frontend && $(NPM) run dev

notebook: ## Open Jupyter Lab with the training notebook
	$(JUPYTER) notebooks/house_price_model.ipynb

# ─── Dataset ─────────────────────────────────────────────────────────────────
download-data: ## Download the Kaggle dataset into notebooks/data/
	mkdir -p notebooks/data
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
	rm -rf .venv __pycache__ *.egg-info build dist
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

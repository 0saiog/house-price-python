.PHONY: setup dev backend frontend test clean download-data help

# ─── Defaults ────────────────────────────────────────────────────────────────
PYTHON   ?= python
PIP      ?= $(PYTHON) -m pip
NODE     ?= node
NPM      ?= npm
JUPYTER  ?= $(PYTHON) -m jupyter lab

HELP_WIDTH = 22

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-$(HELP_WIDTH)s\033[0m %s\n", $$1, $$2}'

# ─── Setup ───────────────────────────────────────────────────────────────────
setup: ## Full setup: venv + deps + editable install + frontend
	$(PYTHON) -m venv .venv
	@echo "Run 'source .venv/bin/activate' (Linux/macOS) or '.venv\\Scripts\\activate' (Windows)"
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	cd frontend && $(NPM) install
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@cp -n frontend/.env.example frontend/.env 2>/dev/null || true
	@echo "\nDone. Activate your venv, then run 'make dev'."

# ─── Development ─────────────────────────────────────────────────────────────
dev: ## Start backend and frontend dev servers (background)
	$(MAKE) backend & $(MAKE) frontend

backend: ## Start the FastAPI backend (port 8000)
	cd backend && uvicorn app.main:app --reload

frontend: ## Start the Vite frontend dev server (port 5173)
	cd frontend && $(NPM) run dev

notebook: ## Open Jupyter Lab with the training notebook
	$(JUPYTER) notebooks/house_price_model.ipynb

# ─── Dataset ─────────────────────────────────────────────────────────────────
download-data: ## Download the Kaggle dataset into notebooks/data/
	mkdir -p notebooks/data
	@echo "Downloading from Kaggle..."
	$(PYTHON) -c "\
	import urllib.request, zipfile, io, os; \
	url = 'https://www.kaggle.com/api/v1/datasets/download/juhibhojani/house-price'; \
	data = urllib.request.urlopen(url).read(); \
	z = zipfile.ZipFile(io.BytesIO(data)); \
	z.extractall('notebooks/data'); \
	print('Extracted to notebooks/data/')"

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
	docker run -p 8000:8000 house-price-api

# ─── Cleanup ─────────────────────────────────────────────────────────────────
clean: ## Remove build artifacts
	rm -rf .venv __pycache__ *.egg-info build dist
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

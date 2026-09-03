# House Price Prediction

Predicts what a flat or house in India is worth from its city, floor area, layout and condition.
Trained on 187,531 real listings with pandas + scikit-learn, served by FastAPI, with a React form on top.

**Stack:** Python 3.11+ · pandas · scikit-learn · FastAPI · React 19 · TypeScript · Vite

---

## Quick start

### Option 1 — Docker (any OS, easiest)

Requires [Docker Desktop](https://docs.docker.com/get-docker/) or Docker Engine.

```bash
git clone https://github.com/0saiog/house-price-python.git
cd house-price-python

# Copy env files
cp backend/.env.example backend/.env   # Windows PowerShell: Copy-Item backend\.env.example backend\.env

# Start the API
docker compose up --build
# API at http://localhost:8000  |  Swagger at http://localhost:8000/docs
```

The Docker image bundles the trained model, so no dataset download or notebook run is needed.

For the **frontend**, use the native setup below (Option 2 or 3).

### Option 2 — Setup script (Linux / macOS / Git Bash)

```bash
git clone https://github.com/0saiog/house-price-python.git
cd house-price-python
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
make dev
```

### Option 3 — Setup script (Windows PowerShell)

```powershell
git clone https://github.com/0saiog/house-price-python.git
cd house-price-python
.\setup.ps1
.venv\Scripts\Activate.ps1
make dev
```

### Option 4 — Manual (any platform)

#### Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js + npm | 18+ | `node --version` |
| Git | any recent | `git --version` |

#### Step 1 — Python environment

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .
```

**Windows (cmd):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements-dev.txt
pip install -e .
```

> **`pip install -e .` is required.** The backend imports `house_price` as a package;
> without the editable install, `uvicorn` cannot find it.

#### Step 2 — .env files

**Linux / macOS:**

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Windows (PowerShell):**

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

#### Step 3 — Dataset (only if retraining)

The trained model is committed, so the API works without downloading the dataset.

**Linux / macOS:**

```bash
mkdir -p notebooks/data
curl -L -o /tmp/house-price.zip \
  "https://www.kaggle.com/api/v1/datasets/download/juhibhojani/house-price"
unzip -o /tmp/house-price.zip -d notebooks/data
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path notebooks\data
Invoke-WebRequest `
  -Uri "https://www.kaggle.com/api/v1/datasets/download/juhibhojani/house-price" `
  -OutFile "$env:TEMP\house-price.zip"
Expand-Archive -Path "$env:TEMP\house-price.zip" -DestinationPath notebooks\data -Force
```

**Windows (with included downloader):**

Run `assets\download.exe` from the repo root — it fetches the dataset into `notebooks\data\`.

Source: [kaggle.com/datasets/juhibhojani/house-price](https://www.kaggle.com/datasets/juhibhojani/house-price) (102 MB, 187,531 rows).

#### Step 4 — Notebook (optional)

```bash
jupyter lab notebooks/house_price_model.ipynb    # Kernel → Restart & Run All
```

Takes about a minute. Writes `models/` and `reports/`.

#### Step 5 — Backend

**Linux / macOS:**

```bash
cd backend && uvicorn app.main:app --reload
```

**Windows (PowerShell):**

```powershell
cd backend; uvicorn app.main:app --reload
```

**Windows (cmd):**

```cmd
cd backend
uvicorn app.main:app --reload
```

API at <http://localhost:8000> · Swagger at <http://localhost:8000/docs>

#### Step 6 — Frontend

**Linux / macOS:**

```bash
cd frontend && npm install && npm run dev
```

**Windows (PowerShell / cmd):**

```powershell
cd frontend; npm install; npm run dev
```

Frontend at <http://localhost:5173>

---

## Running tests

```bash
# Backend (8 API tests against the real model)
cd backend && python -m pytest -v

# Frontend (type-check + production build)
cd frontend && npm run build
```

## Docker

### Build and run manually

```bash
docker build -f backend/Dockerfile -t house-price-api .
docker run -p 8000:8000 --env-file backend/.env house-price-api
```

### Docker Compose

```bash
docker compose up --build
```

The `docker-compose.yml` starts the API on port 8000 with health checks.
For development with hot-reload, use the native setup instead.

### What the image contains

- Python 3.12 slim base
- All backend dependencies (pinned to match the trained model)
- The trained model (`models/house_price.pkl`) and location list
- The shared `house_price` package
- A non-root `app` user
- A health check endpoint at `/health`

---

## Environment variables

### `backend/.env`

| Variable | Default | Purpose |
|---|---|---|
| `HOST` | `127.0.0.1` | Bind address (`0.0.0.0` in Docker) |
| `PORT` | `8000` | Bind port |
| `MODEL_PATH` | `models/house_price.pkl` | Exported pipeline (resolved from repo root) |
| `LOCATIONS_PATH` | `models/locations.json` | City list |
| `ALLOWED_ORIGIN` | `http://localhost:5173` | CORS allowed origin |
| `LOG_LEVEL` | `INFO` | Python log level |

### `frontend/.env`

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | API base URL (only `VITE_` prefix reaches the browser) |

---

## API reference

### `GET /health`

```json
{ "status": "ok", "model_loaded": true, "model_name": "ClippedRegressor", "sklearn_version": "1.9.0" }
```

### `GET /locations`

Returns the cities the model was trained on. The frontend dropdown is populated from here.

### `POST /predict`

| Field | Type | Required | Notes |
|---|---|---|---|
| `location` | string | yes | A city from `/locations` |
| `area_sqft` | number | yes | 0 < area ≤ 1,000,000 |
| `furnishing` | enum | no | `Furnished` / `Semi-Furnished` / `Unfurnished` |
| `transaction` | enum | no | `Resale` / `New Property` |
| `is_carpet_area` | boolean | no | Default `true` |
| `bathroom`, `balcony`, `car_parking` | number | no | Imputed with training median if omitted |
| `floor_num`, `total_floors` | number | no | Ground floor is `0` |
| `ownership`, `facing` | string | no | Encodes as `missing` if omitted |
| `parking_covered`, `overlooking_garden`, `overlooking_pool`, `overlooking_main_road` | boolean | no | Default `false` |

**Example:**

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "location": "mumbai",
    "area_sqft": 1200,
    "furnishing": "Semi-Furnished",
    "transaction": "Resale",
    "bathroom": 2,
    "balcony": 1,
    "floor_num": 3,
    "total_floors": 10,
    "car_parking": 1,
    "parking_covered": true
  }'
```

**Response:**

```json
{
  "predicted_price": 20964228.25,
  "predicted_price_formatted": "2.10 Cr",
  "currency": "INR",
  "location_known": true
}
```

`location_known` is `false` when the city was not in the training data.

**Errors:** `422 Unprocessable Entity` for invalid input (negative area, blank city, floor above building top).

---

## Project structure

```
.
├── house_price/                # shared package (notebook + backend import this)
│   ├── cleaning.py             # text parsers: amount, area, floor, parking, ...
│   └── model.py                # ClippedRegressor, SmearedRegressor
├── notebooks/
│   ├── house_price_model.ipynb # full analysis, runs top to bottom
│   └── data/                   # gitignored — see Dataset section
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app + CORS + model loading
│   │   ├── api/routes/         # GET /health, GET /locations, POST /predict
│   │   ├── core/config.py      # pydantic-settings, reads .env
│   │   ├── schemas/            # request / response models
│   │   ├── services/           # inference engine + preprocessing
│   │   └── utils/              # logging config
│   ├── tests/                  # pytest integration tests
│   ├── requirements.txt        # pinned runtime deps
│   ├── .env.example
│   └── Dockerfile
├── frontend/                   # React + TypeScript + Vite
├── models/                     # house_price.pkl, locations.json, metrics.json
├── reports/                    # plots saved by the notebook
├── assets/                     # Windows dataset downloader
├── docker-compose.yml          # one-command Docker start
├── Makefile                    # cross-platform build targets
├── setup.sh                    # Linux / macOS setup script
├── setup.ps1                   # Windows PowerShell setup script
├── pyproject.toml              # makes house_price importable
└── requirements-dev.txt        # notebook + plotting deps
```

## Make targets

Run `make help` to list all available targets:

| Target | Description |
|---|---|
| `make setup` | Full setup: venv + deps + frontend |
| `make dev` | Start backend + frontend |
| `make backend` | Start FastAPI only |
| `make frontend` | Start Vite dev server only |
| `make test` | Run all tests |
| `make test-backend` | Run pytest |
| `make test-frontend` | TypeScript check + build |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker image |
| `make docker-up` | docker compose up --build |
| `make download-data` | Fetch Kaggle dataset |
| `make clean` | Remove build artifacts |

> **Windows note:** `make` is not installed by default. Install it via
> `winget install GnuWin32.Make` or use the setup scripts / Docker instead.

---

## Results

Gradient boosting, trained on `log1p(price)`, scored on a held-out test split of 12,530 listings:

| model | MAE | RMSE | R² | MdAPE | pickle | fit |
|---|---|---|---|---|---|---|
| *Rate card (city median × area)* | *₹32.41 Lac* | *₹71.87 Lac* | *0.647* | *24.1%* | – | – |
| Linear regression | ₹27.15 Lac | ₹61.05 Lac | 0.745 | 20.6% | 0.0 MB | 1.0s |
| MLP 128-64 | ₹25.98 Lac | ₹61.26 Lac | 0.744 | 19.5% | 0.6 MB | 19.8s |
| **Gradient boosting** | **₹23.01 Lac** | **₹49.72 Lac** | **0.831** | **17.5%** | 1.5 MB | 3.6s |
| Random forest | ₹23.64 Lac | ₹50.53 Lac | 0.826 | 17.3% | 393.7 MB | 16.9s |

Five-fold cross validation gives mean R² **0.816** (sd 0.016).

## Limitations

A typical prediction is 17.5% out — too loose to price a flat precisely. The bottleneck is
`location`: it's city-level, and in Indian property the neighbourhood matters. Two 1,000 sqft
flats in Mumbai can differ 3x between Bandra and Bhiwandi. The neighbourhood is in the listing
`Title` and `Description`, neither of which is used here — pulling it out is the obvious next step.

## License

See repository for license details.

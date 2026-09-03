FROM python:3.12-slim AS base

# Prevent .pyc files and enable unbuffered output for Docker logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Dependencies (cached unless requirements change) ──────────────────────
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Application code ──────────────────────────────────────────────────────
COPY house_price/ ./house_price/
COPY backend/app/ ./backend/app/
COPY models/      ./models/

# Non-root user for production.
RUN groupadd --gid 10001 app && \
    useradd  --uid 10001 --gid app --create-home app && \
    chown -R app:app /app
USER app

# ── Runtime config ────────────────────────────────────────────────────────
ENV HOST=0.0.0.0 \
    PORT=8000 \
    MODEL_PATH=/app/models/house_price.pkl \
    LOCATIONS_PATH=/app/models/locations.json \
    PYTHONPATH=/app:/app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]

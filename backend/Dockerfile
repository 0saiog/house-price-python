# Built from the repository root so the image can copy both `backend/` and the
# shared `house_price/` package the service imports:
#     docker build -f backend/Dockerfile -t house-price-api .

FROM python:3.12-slim AS base
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencies first, so an edit to the source does not reinstall scikit-learn.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY house_price ./house_price
COPY backend/app ./backend/app
COPY models ./models

RUN useradd --create-home --uid 10001 app && chown -R app /app
USER app

ENV HOST=0.0.0.0 \
    PORT=8000 \
    MODEL_PATH=/app/models/house_price.pkl \
    LOCATIONS_PATH=/app/models/locations.json \
    PYTHONPATH=/app:/app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]

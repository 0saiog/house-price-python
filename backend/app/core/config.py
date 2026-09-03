"""Settings, read from the environment with a `.env` file as the fallback."""

from __future__ import annotations

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Repository root, three levels above this file's package.
ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Everything the service needs to start.

    Nothing here is secret, but the paths and the allowed origin change between
    a laptop and a container, so none of them are hard-coded.
    """

    model_config = SettingsConfigDict(
        # Both locations are tried: `backend/.env` when the service is started
        # from the repository root, `.env` when started from inside `backend/`.
        env_file=(ROOT / "backend" / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8000
    model_path: Path = ROOT / "models" / "house_price.pkl"
    locations_path: Path = ROOT / "models" / "locations.json"
    allowed_origin: str = "http://localhost:5173"
    log_level: str = "INFO"

    @field_validator("model_path", "locations_path")
    @classmethod
    def _resolve_against_root(cls, value: Path) -> Path:
        """Resolve a relative path against the repository root, not the cwd.

        `.env` naturally holds `models/house_price.pkl`, which only resolves if
        the process happens to start at the repository root - so `uvicorn` run
        from `backend/`, and pytest, would silently fall back to a path that
        does not exist. Anchoring to the root makes the setting mean the same
        thing wherever the service is started from.
        """
        return value if value.is_absolute() else ROOT / value


settings = Settings()

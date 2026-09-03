"""Logging setup."""

from __future__ import annotations

import logging


def configure(level: str = "INFO") -> None:
    """Install a plain, readable log format. Safe to call more than once."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )

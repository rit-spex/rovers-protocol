"""Loads and caches protocol.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore[import-not-found]


@lru_cache(maxsize=1)
def load_protocol_definition() -> Dict[str, Any]:
    """Load and cache protocol.yaml from the repository root."""
    schema_path = Path(__file__).resolve().parents[1] / "protocol.yaml"
    if not schema_path.exists():
        raise FileNotFoundError(f"Protocol schema not found: {schema_path}")

    with schema_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    if not isinstance(data, dict):
        raise ValueError("protocol.yaml must deserialize into a mapping")

    if "messages" not in data or "data_types" not in data:
        raise ValueError("protocol.yaml must define both 'messages' and 'data_types'")

    return data

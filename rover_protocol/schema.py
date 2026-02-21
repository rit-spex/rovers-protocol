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

    required_sections = (
        "messages",
        "data_types",
        "timing",
        "communication",
        "controllers",
        "controller_modes",
        "auto_states",
    )
    missing = [section for section in required_sections if section not in data]
    if missing:
        raise ValueError(
            "protocol.yaml missing required sections: " + ", ".join(missing)
        )

    for section in required_sections:
        if not isinstance(data[section], dict):
            raise ValueError(f"protocol.yaml section '{section}' must be a mapping")

    return data

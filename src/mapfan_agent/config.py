"""Configuration for mapfan-agent CLI."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]


@dataclass
class Config:
    api_url: str = "http://localhost:8000"
    api_key: str = ""


def load_config(
    config_path: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> Config:
    """Load config: defaults -> TOML -> env overrides."""
    import os

    config = Config()

    # TOML file
    if config_path is None:
        default_path = Path.home() / ".mapfan-agent" / "config.toml"
        if default_path.exists():
            config_path = default_path
    if config_path and config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        if "api" in data:
            if "url" in data["api"]:
                config.api_url = data["api"]["url"]
            if "key" in data["api"]:
                config.api_key = data["api"]["key"]

    # Environment variables
    env = env_overrides if env_overrides is not None else dict(os.environ)
    if "MAPFAN_API_URL" in env:
        config.api_url = env["MAPFAN_API_URL"]
    if "MAPFAN_API_KEY" in env:
        config.api_key = env["MAPFAN_API_KEY"]

    return config

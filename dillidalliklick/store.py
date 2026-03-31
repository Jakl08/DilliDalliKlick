"""Persistent JSON-based data store for DilliDalliKlick."""

import json
import os
import sys
from pathlib import Path


def _data_dir() -> Path:
    """Return the platform-appropriate user-data directory."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "DilliDalliKlick"


_DATA_FILE = _data_dir() / "data.json"

_DEFAULT: dict = {"photobooks": {}}


def load() -> dict:
    """Load application data from disk, returning defaults if missing."""
    if not _DATA_FILE.exists():
        return dict(_DEFAULT)
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "photobooks" not in data:
            data["photobooks"] = {}
        return data
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT)


def save(data: dict) -> None:
    """Persist application data to disk."""
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

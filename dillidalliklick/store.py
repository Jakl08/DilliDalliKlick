"""Persistent JSON-based data store for DilliDalliKlick."""

import copy
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, TypedDict, cast
from dillidalliklick.constants import strings

_lock = threading.Lock()

class StoreData(TypedDict):
    photobooks: dict[str, Any]

def _data_dir() -> Path:
    """Return the platform-appropriate user-data directory."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / strings.APP_NAME

_DATA_FILE: Path = _data_dir() / "data.json"

_DEFAULT: StoreData = {
    "photobooks": {}
}

def load() -> StoreData:
    """Load application data from disk, returning defaults if missing."""
    with _lock:
        if not _DATA_FILE.exists():
            return copy.deepcopy(_DEFAULT)
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                data = cast(StoreData, json.load(f))
            if "photobooks" not in data:
                data["photobooks"] = {}
            return data 
        except (json.JSONDecodeError, OSError):
            return copy.deepcopy(_DEFAULT)


def save(data: StoreData) -> None:
    """Persist application data to disk."""
    with _lock:
        _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", dir=_DATA_FILE.parent, delete=False,
                suffix=".tmp", encoding="utf-8"
            ) as tmp:
                json.dump(data, tmp, indent=2, ensure_ascii=False)
                tmp_path = Path(tmp.name)
            tmp_path.replace(_DATA_FILE)
        finally:
            if tmp_path is not None: tmp_path.unlink(missing_ok=True)
"""Photobook/domain logic isolated from UI widgets."""

import os
import time
from pathlib import Path
from typing import Any

from dillidalliklick import store
from dillidalliklick.store import StoreData

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


class PhotobookLogic:
    """Owns photobook CRUD and photo import/scan operations."""

    def __init__(self, state: StoreData) -> None:
        self._state = state

    def books(self) -> list[tuple[str, str, int]]:
        """Return tuples of (book_id, name, photo_count) for list rendering."""
        result: list[tuple[str, str, int]] = []
        for book_id, book in self._state.get("photobooks", {}).items():
            result.append((book_id, str(book.get("name", book_id)), len(book.get("photos", []))))
        return result

    def create_book(self, name: str) -> str | None:
        clean = name.strip()
        if not clean:
            return None

        book_id = f"book_{int(time.time() * 1000)}"
        self._state["photobooks"][book_id] = {
            "id": book_id,
            "name": clean,
            "photos": [],
            "directory": None,
        }
        self._save()
        return book_id

    def delete_book(self, book_id: str) -> bool:
        book = self._state.get("photobooks", {}).get(book_id)
        if not book:
            return False
        del self._state["photobooks"][book_id]
        self._save()
        return True

    def get_book(self, book_id: str | None) -> dict[str, Any] | None:
        if book_id is None:
            return None
        return self._state.get("photobooks", {}).get(book_id)

    def set_book_directory(self, book_id: str, dir_path: str) -> None:
        book = self._require_book(book_id)
        book["directory"] = dir_path
        images = self._scan_directory(dir_path)
        existing = set(book.get("photos", []))
        book["photos"] = list(existing | set(images))
        self._save()

    def refresh_book_directory(self, book_id: str) -> int:
        book = self._require_book(book_id)
        directory = book.get("directory")
        if not directory:
            return 0

        images = self._scan_directory(directory)
        existing = set(book.get("photos", []))
        new_images = set(images) - existing
        book["photos"] = list(existing | set(images))
        self._save()
        return len(new_images)

    def import_photos(self, book_id: str, paths: list[str]) -> int:
        book = self._require_book(book_id)
        existing = set(book.get("photos", []))
        added = [p for p in paths if p not in existing]
        book["photos"] = list(existing | set(paths))
        self._save()
        return len(added)

    def remove_photo(self, book_id: str, path: str) -> None:
        book = self._require_book(book_id)
        book["photos"] = [p for p in book.get("photos", []) if p != path]
        self._save()

    def _require_book(self, book_id: str) -> dict[str, Any]:
        book = self._state.get("photobooks", {}).get(book_id)
        if not book:
            raise ValueError("Fotobuch nicht gefunden")
        return book

    def _scan_directory(self, dir_path: str) -> list[str]:
        result: list[str] = []
        try:
            for entry in os.scandir(dir_path):
                if entry.is_file() and Path(entry.path).suffix.lower() in IMAGE_EXTENSIONS:
                    result.append(entry.path)
        except OSError:
            pass
        return result

    def _save(self) -> None:
        store.save(self._state)

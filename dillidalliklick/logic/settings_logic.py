"""Settings/business logic for building game configuration."""

from dillidalliklick.logic.game_logic import GameConfig
from dillidalliklick.store import StoreData


class SettingsLogic:
    """Encapsulates settings-derived game configuration rules."""

    def __init__(self, state: StoreData) -> None:
        self._state = state

    def book_options(self) -> list[tuple[str, str, int]]:
        """Return tuples of (book_id, name, photo_count) for the UI selector."""
        options: list[tuple[str, str, int]] = []
        for book_id, book in self._state.get("photobooks", {}).items():
            photos = list(book.get("photos", []))
            options.append((book_id, str(book.get("name", book_id)), len(photos)))
        return options

    def build_game_config(
        self,
        book_id: str | None,
        photo_count: int,
        cols: int,
        rows: int,
        timer_mode: bool,
        interval: int,
    ) -> GameConfig:
        """Validate settings and produce a typed game config."""
        if book_id is None:
            raise ValueError("Bitte ein Fotobuch auswählen.")

        book = self._state.get("photobooks", {}).get(book_id)
        if not book or not book.get("photos"):
            raise ValueError("Das gewählte Fotobuch enthält keine Fotos.")

        return {
            "book_id": book_id,
            "photos": list(book["photos"]),
            "photo_count": photo_count,
            "cols": cols,
            "rows": rows,
            "mode": "timer" if timer_mode else "click",
            "interval": interval,
        }

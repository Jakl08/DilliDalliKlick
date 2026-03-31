"""Gameplay session logic extracted from the UI layer."""

import random
from typing import TypedDict


class GameConfig(TypedDict):
    """Configuration values required to start one game session."""

    book_id: str
    photos: list[str]
    photo_count: int
    cols: int
    rows: int
    mode: str
    interval: int


class GameSession:
    """Owns non-UI gameplay state and rules."""

    def __init__(self) -> None:
        self._config: GameConfig | None = None
        self._photos: list[str] = []
        self._photo_index = 0

    def start(self, config: GameConfig) -> None:
        """Initialize a new game session from config."""
        self._config = config
        photos = list(config["photos"])
        random.shuffle(photos)
        self._photos = photos[: min(config["photo_count"], len(photos))]
        self._photo_index = 0

    @property
    def total_photos(self) -> int:
        return len(self._photos)

    @property
    def current_index(self) -> int:
        return self._photo_index

    @property
    def cols(self) -> int:
        return self._require_config()["cols"]

    @property
    def rows(self) -> int:
        return self._require_config()["rows"]

    @property
    def mode(self) -> str:
        return self._require_config()["mode"]

    @property
    def interval(self) -> int:
        return self._require_config()["interval"]

    @property
    def mode_label(self) -> str:
        if self.mode == "click":
            return "Klick"
        return f"Timer ({self.interval}s)"

    def set_photo_index(self, index: int) -> bool:
        """Set active photo index. Returns False if index is out of bounds."""
        if index < 0 or index >= len(self._photos):
            return False
        self._photo_index = index
        return True

    def current_photo_path(self) -> str | None:
        if not self._photos:
            return None
        return self._photos[self._photo_index]

    def is_last_photo(self) -> bool:
        return (self._photo_index + 1) >= len(self._photos)

    def timer_reset(self) -> int:
        return self.interval

    def timer_tick(self, remaining: int) -> tuple[int, bool]:
        """Advance one timer tick and indicate whether a tile should be revealed."""
        remaining -= 1
        if remaining <= 0:
            return self.interval, True
        return remaining, False

    def _require_config(self) -> GameConfig:
        if self._config is None:
            raise RuntimeError("GameSession is not initialized. Call start() first.")
        return self._config


class BoardState:
    """Owns tile reveal matrix and related board rules."""

    def __init__(self, cols: int, rows: int) -> None:
        self._cols = cols
        self._rows = rows
        self._revealed: list[list[bool]] = []
        self.reset(cols, rows)

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    def reset(self, cols: int, rows: int) -> None:
        self._cols = cols
        self._rows = rows
        self._revealed = [[False] * cols for _ in range(rows)]

    def is_revealed(self, row: int, col: int) -> bool:
        return self._revealed[row][col]

    def reveal(self, row: int, col: int) -> bool:
        if self._revealed[row][col]:
            return False
        self._revealed[row][col] = True
        return True

    def revealed_count(self) -> int:
        return sum(1 for row in self._revealed for cell in row if cell)

    def is_complete(self) -> bool:
        return all(cell for row in self._revealed for cell in row)

    def random_unrevealed(self) -> tuple[int, int] | None:
        candidates = [
            (r, c)
            for r in range(self._rows)
            for c in range(self._cols)
            if not self._revealed[r][c]
        ]
        if not candidates:
            return None
        return random.choice(candidates)

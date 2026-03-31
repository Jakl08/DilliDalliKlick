"""Game window – the photo reveal gameplay screen."""

import random

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class GameWindow(QMainWindow):
    """Gameplay screen: photo reveal with click or timer mode."""

    def __init__(self, config: dict, parent_window) -> None:
        super().__init__()
        self._config = config
        self._parent_window = parent_window
        self.setWindowTitle("DilliDalliKlick – Spiel")
        self.setMinimumSize(900, 680)

        # Pick and shuffle photos
        photos = list(config["photos"])
        random.shuffle(photos)
        self._photos = photos[: min(config["photo_count"], len(photos))]
        self._photo_index = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._timer_tick)
        self._timer_remaining = 0

        self._build_ui()
        self._load_photo(0)

    # ------------------------------------------------------------------
    # UI skeleton
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#0d0d1a; border-bottom:1px solid #1e3a5f;")
        toolbar.setFixedHeight(52)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 0, 16, 0)

        brand = QLabel("🎮  DilliDalliKlick")
        brand_font = QFont()
        brand_font.setPointSize(13)
        brand_font.setBold(True)
        brand.setFont(brand_font)
        brand.setStyleSheet("color:#e94560;")
        tb.addWidget(brand)
        tb.addStretch()

        settings_btn = QPushButton("⚙️  Einstellungen")
        settings_btn.clicked.connect(self._back_to_settings)
        tb.addWidget(settings_btn)

        menu_btn = QPushButton("🏠  Menü")
        menu_btn.clicked.connect(self._back_to_menu)
        tb.addWidget(menu_btn)

        # Info bar
        info_bar = QWidget()
        info_bar.setStyleSheet("background:#111122;")
        info_bar.setFixedHeight(36)
        ib = QHBoxLayout(info_bar)
        ib.setContentsMargins(20, 0, 20, 0)
        ib.setSpacing(24)

        self._photo_lbl = QLabel()
        self._photo_lbl.setStyleSheet("color:#a0a0b0; font-size:13px;")
        ib.addWidget(self._photo_lbl)

        self._tiles_lbl = QLabel()
        self._tiles_lbl.setStyleSheet("color:#a0a0b0; font-size:13px;")
        ib.addWidget(self._tiles_lbl)

        self._mode_lbl = QLabel()
        self._mode_lbl.setStyleSheet("color:#a0a0b0; font-size:13px;")
        ib.addWidget(self._mode_lbl)

        ib.addStretch()

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)

        # Central board
        self._board_container = QWidget()
        self._board_container.setStyleSheet("background:#000;")
        board_layout = QVBoxLayout(self._board_container)
        board_layout.setContentsMargins(16, 16, 16, 16)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._board_widget = _GameBoard(self._config["cols"], self._config["rows"])
        self._board_widget.tile_clicked.connect(self._on_tile_clicked)
        board_layout.addWidget(self._board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls bar
        controls = QWidget()
        controls.setStyleSheet("background:#0d0d1a; border-top:1px solid #1e3a5f;")
        controls.setFixedHeight(60)
        ctrl = QHBoxLayout(controls)
        ctrl.setContentsMargins(20, 0, 20, 0)
        ctrl.setSpacing(16)

        self._timer_lbl = QLabel("")
        self._timer_lbl.setStyleSheet("color:#e94560; font-size:22px; font-weight:700; min-width:70px;")
        ctrl.addWidget(self._timer_lbl)

        ctrl.addStretch()

        self._hint_lbl = QLabel("")
        self._hint_lbl.setStyleSheet("color:#606070; font-size:13px;")
        ctrl.addWidget(self._hint_lbl)

        self._next_btn = QPushButton("Nächstes Foto  ➜")
        self._next_btn.setProperty("class", "success")
        self._next_btn.setFixedHeight(38)
        self._next_btn.setVisible(False)
        self._next_btn.clicked.connect(self._next_photo)
        ctrl.addWidget(self._next_btn)

        self._finish_btn = QPushButton("🏁  Spiel beenden")
        self._finish_btn.setProperty("class", "primary")
        self._finish_btn.setFixedHeight(38)
        self._finish_btn.setVisible(False)
        self._finish_btn.clicked.connect(self._show_game_over)
        ctrl.addWidget(self._finish_btn)

        # Root
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(toolbar)
        root_layout.addWidget(info_bar)
        root_layout.addWidget(self._progress)
        root_layout.addWidget(self._board_container, 1)
        root_layout.addWidget(controls)
        self.setCentralWidget(root)

    # ------------------------------------------------------------------
    # Photo loading
    # ------------------------------------------------------------------

    def _load_photo(self, index: int) -> None:
        self._stop_timer()
        self._next_btn.setVisible(False)
        self._finish_btn.setVisible(False)

        if index >= len(self._photos):
            self._show_game_over()
            return

        self._photo_index = index
        path = self._photos[index]
        pixmap = QPixmap(path)
        if pixmap.isNull():
            # Try next photo
            QMessageBox.warning(self, "Fehler", f"Bild konnte nicht geladen werden:\n{path}")
            self._load_photo(index + 1)
            return

        cols = self._config["cols"]
        rows = self._config["rows"]
        self._board_widget.set_photo(pixmap, cols, rows)
        self._progress.setValue(0)

        mode = self._config["mode"]
        if mode == "click":
            self._hint_lbl.setText("Klicke auf die Felder, um sie aufzudecken")
            self._timer_lbl.setText("")
        else:
            self._hint_lbl.setText("")
            self._timer_remaining = self._config["interval"]
            self._timer_lbl.setText(f"{self._timer_remaining}s")
            self._timer.start(1000)

        mode_text = "Klick" if mode == "click" else f"Timer ({self._config['interval']}s)"
        self._mode_lbl.setText(f"Modus: <b style='color:#eaeaea'>{mode_text}</b>")
        self._update_info()

    def _update_info(self) -> None:
        total = len(self._photos)
        idx = self._photo_index
        self._photo_lbl.setText(f"Foto: <b style='color:#eaeaea'>{idx + 1} / {total}</b>")
        revealed = self._board_widget.revealed_count()
        total_tiles = self._config["cols"] * self._config["rows"]
        self._tiles_lbl.setText(
            f"Aufgedeckt: <b style='color:#eaeaea'>{revealed} / {total_tiles}</b>"
        )
        self._photo_lbl.update()
        pct = int(revealed / total_tiles * 100) if total_tiles else 0
        self._progress.setValue(pct)

    # ------------------------------------------------------------------
    # Tile reveal
    # ------------------------------------------------------------------

    def _on_tile_clicked(self, row: int, col: int) -> None:
        if self._config["mode"] != "click":
            return
        self._reveal_tile_rc(row, col)

    def _reveal_tile_rc(self, row: int, col: int) -> None:
        changed = self._board_widget.reveal(row, col)
        if changed:
            self._update_info()
            if self._board_widget.is_complete():
                self._on_complete()

    def _reveal_random_tile(self) -> None:
        pos = self._board_widget.random_unrevealed()
        if pos is None:
            return
        self._reveal_tile_rc(*pos)

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------

    def _timer_tick(self) -> None:
        self._timer_remaining -= 1
        self._timer_lbl.setText(f"{self._timer_remaining}s")
        if self._timer_remaining <= 0:
            self._timer_remaining = self._config["interval"]
            self._reveal_random_tile()

    def _stop_timer(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        self._timer_lbl.setText("")

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

    def _on_complete(self) -> None:
        self._stop_timer()
        self._hint_lbl.setText("")
        self._progress.setValue(100)
        is_last = (self._photo_index + 1) >= len(self._photos)
        self._next_btn.setVisible(not is_last)
        self._finish_btn.setVisible(is_last)

    def _next_photo(self) -> None:
        self._load_photo(self._photo_index + 1)

    def _show_game_over(self) -> None:
        self._stop_timer()
        self._next_btn.setVisible(False)
        self._finish_btn.setVisible(False)
        self._board_widget.show_game_over(len(self._photos))
        self._hint_lbl.setText("")
        self._timer_lbl.setText("")
        self._progress.setValue(100)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _back_to_settings(self) -> None:
        self._stop_timer()
        self._parent_window.show()
        self.close()

    def _back_to_menu(self) -> None:
        self._stop_timer()
        # Walk up to the menu window
        win = self._parent_window
        while hasattr(win, "_parent_window"):
            win = win._parent_window
        win.show()
        self.close()

    def closeEvent(self, event):
        self._stop_timer()
        self._parent_window.show()
        super().closeEvent(event)


# ──────────────────────────────────────────────────────────────────────
# _GameBoard – custom widget that renders the photo + tile overlay
# ──────────────────────────────────────────────────────────────────────

class _GameBoard(QWidget):
    """
    Displays a photo covered by an opaque grid of tiles.
    Tiles are revealed one at a time (drawn transparently).
    """

    tile_clicked = pyqtSignal(int, int)  # row, col

    _TILE_COLOR = QColor(15, 52, 96)          # covered tile
    _TILE_HOVER = QColor(233, 69, 96, 120)    # hover highlight

    def __init__(self, cols: int, rows: int) -> None:
        super().__init__()
        self._cols = cols
        self._rows = rows
        self._pixmap: QPixmap | None = None
        self._revealed: list[list[bool]] = []
        self._hover_rc: tuple[int, int] | None = None
        self._game_over = False
        self._game_over_total = 0
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # Public API --------------------------------------------------------

    def set_photo(self, pixmap: QPixmap, cols: int, rows: int) -> None:
        self._cols = cols
        self._rows = rows
        self._pixmap = pixmap
        self._revealed = [[False] * cols for _ in range(rows)]
        self._hover_rc = None
        self._game_over = False
        self._resize_board()
        self.update()

    def reveal(self, row: int, col: int) -> bool:
        if self._revealed[row][col]:
            return False
        self._revealed[row][col] = True
        self.update()
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

    def show_game_over(self, total_photos: int) -> None:
        self._game_over = True
        self._game_over_total = total_photos
        self.update()

    # Qt events ---------------------------------------------------------

    def resizeEvent(self, event) -> None:
        self._resize_board()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._game_over:
            self._paint_game_over(painter)
            return

        if self._pixmap is None:
            return

        w, h = self.width(), self.height()
        painter.drawPixmap(0, 0, w, h, self._pixmap)

        tile_w = w / self._cols
        tile_h = h / self._rows

        for r in range(self._rows):
            for c in range(self._cols):
                if self._revealed[r][c]:
                    continue
                x = int(c * tile_w)
                y = int(r * tile_h)
                tw = int((c + 1) * tile_w) - x
                th = int((r + 1) * tile_h) - y

                color = (
                    self._TILE_HOVER
                    if self._hover_rc == (r, c)
                    else self._TILE_COLOR
                )
                painter.fillRect(x, y, tw, th, color)
                # subtle grid line
                painter.setPen(QColor(255, 255, 255, 15))
                painter.drawRect(x, y, tw - 1, th - 1)

    def mouseMoveEvent(self, event) -> None:
        if self._pixmap is None or self._game_over:
            return
        rc = self._rc_at(event.position().x(), event.position().y())
        if rc != self._hover_rc:
            self._hover_rc = rc
            self.update()

    def leaveEvent(self, event) -> None:
        self._hover_rc = None
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._pixmap is None or self._game_over:
            return
        rc = self._rc_at(event.position().x(), event.position().y())
        if rc:
            r, c = rc
            if not self._revealed[r][c]:
                self.tile_clicked.emit(r, c)

    # Private helpers ---------------------------------------------------

    def _rc_at(self, x: float, y: float) -> tuple[int, int] | None:
        if self._cols == 0 or self._rows == 0:
            return None
        w, h = self.width(), self.height()
        c = int(x / w * self._cols)
        r = int(y / h * self._rows)
        c = max(0, min(c, self._cols - 1))
        r = max(0, min(r, self._rows - 1))
        return (r, c)

    def _resize_board(self) -> None:
        if self._pixmap is None:
            return
        parent = self.parent()
        if parent is None:
            return
        avail_w = parent.width() - 32
        avail_h = parent.height() - 32
        img_w = self._pixmap.width()
        img_h = self._pixmap.height()
        if img_w == 0 or img_h == 0:
            return
        scale = min(avail_w / img_w, avail_h / img_h, 1.0)
        self.setFixedSize(max(1, int(img_w * scale)), max(1, int(img_h * scale)))

    def _paint_game_over(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), QColor(0, 0, 0, 200))
        painter.setPen(QColor("#4caf50"))
        f = QFont()
        f.setPointSize(28)
        f.setBold(True)
        painter.setFont(f)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            f"🎉 Spiel beendet!\n{self._game_over_total} Foto(s) aufgedeckt",
        )

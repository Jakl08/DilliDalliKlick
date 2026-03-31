"""Game window – the photo reveal gameplay screen."""

from collections.abc import Callable

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from dillidalliklick.logic.game_logic import BoardState, GameConfig, GameSession
from dillidalliklick.constants import theme


class GameWindow(QWidget):
    """Gameplay page: photo reveal with click or timer mode."""

    def __init__(
        self,
        on_back_settings: Callable[[], None],
        on_back_menu: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._on_back_settings = on_back_settings
        self._on_back_menu = on_back_menu

        self._session = GameSession()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._timer_tick)
        self._timer_remaining = 0

        # Register for theme changes
        theme.register_theme_changed_callback(self._on_theme_changed)

        self._build_ui()

    def _on_theme_changed(self) -> None:
        """Refresh stylesheets when theme changes."""
        self._update_stylesheets()

    def _style_menu_button(self) -> None:
        """Ensure the top-right menu button always has readable themed colors."""
        if not hasattr(self, "_menu_btn"):
            return
        self._menu_btn.setStyleSheet(
            "QPushButton {"
            f"background:{theme.ACCENT};"
            f"color:{theme.BUTTON_TEXT_ACCENT};"
            f"border:1px solid {theme.BORDER};"
            "border-radius:6px;"
            "padding:8px 14px;"
            "}"
            "QPushButton:hover {"
            f"background:{theme.ACCENT_HOVER};"
            f"border-color:{theme.ACCENT};"
            "}"
            "QPushButton:pressed {"
            f"background:{theme.ACCENT};"
            f"color:{theme.BUTTON_TEXT_ACCENT};"
            "}"
        )

    def _update_stylesheets(self) -> None:
        """Update all stylesheets to reflect current theme."""
        if not hasattr(self, "_toolbar"):
            return
        self._toolbar.setStyleSheet(
            f"background:{theme.BG_PRIMARY}; border-bottom:1px solid {theme.BORDER};"
        )
        self._brand.setStyleSheet(f"color:{theme.ACCENT};")
        self._info_bar.setStyleSheet(f"background:{theme.BG_SECONDARY};")
        self._photo_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        self._tiles_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        self._mode_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        self._board_container.setStyleSheet(f"background:{theme.BG_PRIMARY};")
        self._controls.setStyleSheet(
            f"background:{theme.BG_PRIMARY}; border-top:1px solid {theme.BORDER};"
        )
        self._timer_lbl.setStyleSheet(
            f"color:{theme.ACCENT}; font-size:22px; font-weight:700; min-width:70px;"
        )
        self._hint_lbl.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:13px;")
        self._style_menu_button()
        for btn in (self._uncover_btn, self._next_btn, self._finish_btn, self._menu_btn):
            style_obj = btn.style()
            if style_obj is not None:
                style_obj.unpolish(btn)
                style_obj.polish(btn)
            btn.update()
        self._board_widget.update()

    def closeEvent(self, event) -> None:
        """Clean up when window is closed."""
        theme.unregister_theme_changed_callback(self._on_theme_changed)
        super().closeEvent(event)

    def start_game(self, config: GameConfig) -> None:
        """Initialize state and start a new game session."""
        self._session.start(config)
        self.setFocus()
        self._load_photo(0)

    def resizeEvent(self, event) -> None:
        self._board_widget.resize_to_fit()
        super().resizeEvent(event)

    # ------------------------------------------------------------------
    # UI skeleton
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Toolbar
        self._toolbar = QWidget()
        self._toolbar.setStyleSheet(
            f"background:{theme.BG_PRIMARY}; border-bottom:1px solid {theme.BORDER};"
        )
        self._toolbar.setFixedHeight(52)
        tb = QHBoxLayout(self._toolbar)
        tb.setContentsMargins(16, 0, 16, 0)

        self._brand = QLabel("🎮  DilliDalliKlick")
        brand_font = QFont()
        brand_font.setPointSize(13)
        brand_font.setBold(True)
        self._brand.setFont(brand_font)
        self._brand.setStyleSheet(f"color:{theme.ACCENT};")
        tb.addWidget(self._brand)
        tb.addStretch()

        self._menu_btn = QPushButton("🏠  Menü")
        self._menu_btn.setProperty("class", "primary")
        self._style_menu_button()
        self._menu_btn.clicked.connect(self._back_to_menu)
        tb.addWidget(self._menu_btn)

        # Info bar
        self._info_bar = QWidget()
        self._info_bar.setStyleSheet(f"background:{theme.BG_SECONDARY};")
        self._info_bar.setFixedHeight(36)
        ib = QHBoxLayout(self._info_bar)
        ib.setContentsMargins(20, 0, 20, 0)
        ib.setSpacing(24)

        self._photo_lbl = QLabel()
        self._photo_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        ib.addWidget(self._photo_lbl)

        self._tiles_lbl = QLabel()
        self._tiles_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        ib.addWidget(self._tiles_lbl)

        self._mode_lbl = QLabel()
        self._mode_lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:13px;")
        ib.addWidget(self._mode_lbl)

        ib.addStretch()

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)

        # Central board
        self._board_container = _BoardArea()
        self._board_container.setStyleSheet(f"background:{theme.BG_PRIMARY};")
        self._board_container.area_clicked.connect(self._on_board_area_clicked)
        board_layout = QVBoxLayout(self._board_container)
        board_layout.setContentsMargins(0, 0, 0, 0)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._board_widget = _GameBoard(1, 1)
        self._board_widget.tile_clicked.connect(self._on_tile_clicked)
        board_layout.addWidget(self._board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls bar
        self._controls = QWidget()
        self._controls.setStyleSheet(
            f"background:{theme.BG_PRIMARY}; border-top:1px solid {theme.BORDER};"
        )
        self._controls.setFixedHeight(60)
        ctrl = QHBoxLayout(self._controls)
        ctrl.setContentsMargins(20, 0, 20, 0)
        ctrl.setSpacing(16)

        self._timer_lbl = QLabel("")
        self._timer_lbl.setStyleSheet(
            f"color:{theme.ACCENT}; font-size:22px; font-weight:700; min-width:70px;"
        )
        ctrl.addWidget(self._timer_lbl)

        ctrl.addStretch()

        self._hint_lbl = QLabel("")
        self._hint_lbl.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:13px;")
        ctrl.addWidget(self._hint_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        ctrl.addStretch()

        self._uncover_btn = QPushButton("Ganzes Foto aufdecken")
        self._uncover_btn.setProperty("class", "success")
        self._uncover_btn.setFixedHeight(38)
        self._uncover_btn.setVisible(True)
        self._uncover_btn.clicked.connect(self._uncover_photo)
        ctrl.addWidget(self._uncover_btn)

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
        self._finish_btn.clicked.connect(self._end_game)
        ctrl.addWidget(self._finish_btn)

        # Root
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._toolbar)
        root_layout.addWidget(self._info_bar)
        root_layout.addWidget(self._progress)
        root_layout.addWidget(self._board_container, 1)
        root_layout.addWidget(self._controls)

    # ------------------------------------------------------------------
    # Photo loading
    # ------------------------------------------------------------------

    def _load_photo(self, index: int) -> None:
        self._stop_timer()
        self._next_btn.setVisible(False)
        self._uncover_btn.setVisible(True)
        self._finish_btn.setVisible(False)

        if not self._session.set_photo_index(index):
            self._end_game()
            return

        path = self._session.current_photo_path()
        if path is None:
            self._end_game()
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            # Try next photo
            QMessageBox.warning(self, "Fehler", f"Bild konnte nicht geladen werden:\n{path}")
            self._load_photo(index + 1)
            return

        cols = self._session.cols
        rows = self._session.rows
        self._board_widget.set_photo(pixmap, cols, rows)
        self._progress.setValue(0)

        mode = self._session.mode
        if mode == "click":
            self._hint_lbl.setText('Klicke oder benutze "Space", "Enter", um ein zufälliges Feld aufzudecken')
            self._timer_lbl.setText("")
        else:
            self._hint_lbl.setText("")
            self._timer_remaining = self._session.timer_reset()
            self._timer_lbl.setText(f"{self._timer_remaining}s")
            self._timer.start(1000)

        self._mode_lbl.setText(
            f"Modus: <b style='color:{theme.TEXT_PRIMARY}'>{self._session.mode_label}</b>"
        )
        self._update_info()

    def _update_info(self) -> None:
        total = self._session.total_photos
        idx = self._session.current_index
        self._photo_lbl.setText(
            f"Foto: <b style='color:{theme.TEXT_PRIMARY}'>{idx + 1} / {total}</b>"
        )
        revealed = self._board_widget.revealed_count()
        total_tiles = self._session.cols * self._session.rows
        self._tiles_lbl.setText(
            f"Aufgedeckt: <b style='color:{theme.TEXT_PRIMARY}'>{revealed} / {total_tiles}</b>"
        )
        self._photo_lbl.update()
        pct = int(revealed / total_tiles * 100) if total_tiles else 0
        self._progress.setValue(pct)

    # ------------------------------------------------------------------
    # Tile reveal
    # ------------------------------------------------------------------

    def _on_tile_clicked(self, row: int, col: int) -> None:
        if self._session.mode != "click":
            return
        self._reveal_random_tile()

    def _on_board_area_clicked(self) -> None:
        if self._session.mode != "click":
            return
        self._reveal_random_tile()

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
        self._timer_remaining, should_reveal = self._session.timer_tick(self._timer_remaining)
        self._timer_lbl.setText(f"{self._timer_remaining}s")
        if should_reveal:
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
        is_last = self._session.is_last_photo()
        self._next_btn.setVisible(not is_last)
        self._uncover_btn.setVisible(False)
        self._finish_btn.setVisible(is_last)

    def _next_photo(self) -> None:
        self._load_photo(self._session.current_index + 1)

    def _uncover_photo(self) -> None:
        cols = self._session.cols
        rows = self._session.rows
        for r in range(rows):
            for c in range(cols):
                self._board_widget.reveal(r, c)
        self._update_info()
        self._on_complete()

    def _end_game(self) -> None:
        self._stop_timer()
        self._next_btn.setVisible(False)
        self._uncover_btn.setVisible(False)
        self._finish_btn.setVisible(False)
        self._hint_lbl.setText("")
        self._timer_lbl.setText("")
        self._progress.setValue(100)
        self._on_back_menu()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _back_to_menu(self) -> None:
        self._stop_timer()
        self._on_back_menu()

    def keyPressEvent(self, event) -> None:
        if self._session.mode == "click" and event.key() in (
            Qt.Key.Key_Space,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self._reveal_random_tile()
            event.accept()
            return
        super().keyPressEvent(event)


# ──────────────────────────────────────────────────────────────────────
# _GameBoard – custom widget that renders the photo + tile overlay
# ──────────────────────────────────────────────────────────────────────

class _GameBoard(QWidget):
    """
    Displays a photo covered by an opaque grid of tiles.
    Tiles are revealed one at a time (drawn transparently).
    """

    tile_clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, cols: int, rows: int) -> None:
        super().__init__()
        self._state = BoardState(cols, rows)
        self._pixmap: QPixmap | None = None
        self._hover_rc: tuple[int, int] | None = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # Public API --------------------------------------------------------

    def set_photo(self, pixmap: QPixmap, cols: int, rows: int) -> None:
        self._state.reset(cols, rows)
        self._pixmap = pixmap
        self._hover_rc = None
        self._resize_board()
        self.update()

    def reveal(self, row: int, col: int) -> bool:
        changed = self._state.reveal(row, col)
        if not changed:
            return False
        self.update()
        return True

    def revealed_count(self) -> int:
        return self._state.revealed_count()

    def is_complete(self) -> bool:
        return self._state.is_complete()

    def random_unrevealed(self) -> tuple[int, int] | None:
        return self._state.random_unrevealed()

    def resize_to_fit(self) -> None:
        self._resize_board()

    # Qt events ---------------------------------------------------------

    def resizeEvent(self, event) -> None:
        self._resize_board()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._pixmap is None:
            return

        w, h = self.width(), self.height()
        painter.drawPixmap(0, 0, w, h, self._pixmap)

        tile_w = w / self._state.cols
        tile_h = h / self._state.rows

        for r in range(self._state.rows):
            for c in range(self._state.cols):
                if self._state.is_revealed(r, c):
                    continue
                x = int(c * tile_w)
                y = int(r * tile_h)
                tw = int((c + 1) * tile_w) - x
                th = int((r + 1) * tile_h) - y

                color = QColor(theme.BG_CARD)
                painter.fillRect(x, y, tw, th, color)
                # subtle grid line
                grid_color = QColor(theme.BORDER)
                grid_color.setAlpha(100)
                painter.setPen(grid_color)
                painter.drawRect(x, y, tw - 1, th - 1)

    def mouseMoveEvent(self, event) -> None:
        if self._pixmap is None:
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
        if self._pixmap is None:
            return
        rc = self._rc_at(event.position().x(), event.position().y())
        if rc:
            r, c = rc
            self.tile_clicked.emit(r, c)

    # Private helpers ---------------------------------------------------

    def _rc_at(self, x: float, y: float) -> tuple[int, int] | None:
        if self._state.cols == 0 or self._state.rows == 0:
            return None
        w, h = self.width(), self.height()
        c = int(x / w * self._state.cols)
        r = int(y / h * self._state.rows)
        c = max(0, min(c, self._state.cols - 1))
        r = max(0, min(r, self._state.rows - 1))
        return (r, c)

    def _resize_board(self) -> None:
        if self._pixmap is None:
            return
        parent = self.parent()
        if parent is None:
            return
        avail_w = max(1, parent.width())
        avail_h = max(1, parent.height())
        img_w = self._pixmap.width()
        img_h = self._pixmap.height()
        if img_w == 0 or img_h == 0:
            return
        scale = min(avail_w / img_w, avail_h / img_h)
        self.setFixedSize(max(1, int(img_w * scale)), max(1, int(img_h * scale)))


class _BoardArea(QWidget):
    """Clickable play area around the board, excluding the top and bottom bars."""

    area_clicked = pyqtSignal()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.area_clicked.emit()
        super().mousePressEvent(event)


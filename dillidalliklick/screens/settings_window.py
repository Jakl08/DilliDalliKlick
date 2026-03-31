"""Settings window – configure game parameters before starting."""

from collections.abc import Callable

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from dillidalliklick.logic.game_logic import GameConfig
from dillidalliklick.logic.settings_logic import SettingsLogic
from dillidalliklick.store import StoreData


class SettingsWindow(QWidget):
    """Game configuration screen."""

    def __init__(
        self,
        app_state: StoreData,
        on_back: Callable[[], None],
        on_start_game: Callable[[GameConfig], None],
    ) -> None:
        super().__init__()
        self._logic = SettingsLogic(app_state)
        self._on_back = on_back
        self._on_start_game = on_start_game
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#16213e; border-bottom:1px solid #1e3a5f;")
        toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)

        back_btn = QPushButton("← Menü")
        back_btn.clicked.connect(self._go_back)
        tb_layout.addWidget(back_btn)

        # Scroll content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(60, 24, 60, 24)
        content_layout.setSpacing(20)

        # ── Photobook section ──
        book_group = QGroupBox("Fotobuch")
        book_layout = QVBoxLayout(book_group)

        self._book_combo = QComboBox()
        self._populate_books()
        book_layout.addWidget(self._book_combo)
        content_layout.addWidget(book_group)

        # ── Photo count ──
        count_group = QGroupBox("Anzahl der Fotos")
        count_layout = QHBoxLayout(count_group)
        count_layout.setSpacing(12)
        count_lbl = QLabel("Fotos pro Durchlauf:")
        count_lbl.setStyleSheet("color:#a0a0b0;")
        count_layout.addWidget(count_lbl)
        self._photo_count_spin = QSpinBox()
        self._photo_count_spin.setRange(1, 500)
        self._photo_count_spin.setValue(5)
        self._photo_count_spin.setFixedWidth(80)
        count_layout.addWidget(self._photo_count_spin)
        count_layout.addStretch()
        content_layout.addWidget(count_group)

        # ── Grid size ──
        grid_group = QGroupBox("Raster (Spalten × Zeilen)")
        grid_layout = QHBoxLayout(grid_group)
        grid_layout.setSpacing(12)

        cols_lbl = QLabel("Spalten:")
        cols_lbl.setStyleSheet("color:#a0a0b0;")
        grid_layout.addWidget(cols_lbl)
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 20)
        self._cols_spin.setValue(4)
        self._cols_spin.setFixedWidth(70)
        grid_layout.addWidget(self._cols_spin)

        grid_layout.addSpacing(20)

        rows_lbl = QLabel("Zeilen:")
        rows_lbl.setStyleSheet("color:#a0a0b0;")
        grid_layout.addWidget(rows_lbl)
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 20)
        self._rows_spin.setValue(3)
        self._rows_spin.setFixedWidth(70)
        grid_layout.addWidget(self._rows_spin)
        grid_layout.addStretch()
        content_layout.addWidget(grid_group)

        # ── Reveal mode ──
        mode_group = QGroupBox("Enthüllungsmodus")
        mode_layout = QVBoxLayout(mode_group)

        self._radio_click = QRadioButton("🖱️  Klick-Modus – Felder werden per Mausklick aufgedeckt")
        self._radio_click.setChecked(True)
        self._radio_timer = QRadioButton("⏱️  Timer-Modus – Felder werden automatisch aufgedeckt")
        mode_layout.addWidget(self._radio_click)
        mode_layout.addWidget(self._radio_timer)

        # Timer interval (only visible in timer mode)
        self._timer_row = QWidget()
        timer_row_layout = QHBoxLayout(self._timer_row)
        timer_row_layout.setContentsMargins(24, 8, 0, 0)
        interval_lbl = QLabel("Intervall (Sekunden):")
        interval_lbl.setStyleSheet("color:#a0a0b0;")
        timer_row_layout.addWidget(interval_lbl)
        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(1, 60)
        self._interval_spin.setValue(3)
        self._interval_spin.setFixedWidth(70)
        timer_row_layout.addWidget(self._interval_spin)
        timer_row_layout.addStretch()
        mode_layout.addWidget(self._timer_row)
        self._timer_row.setVisible(False)

        self._radio_timer.toggled.connect(self._timer_row.setVisible)

        content_layout.addWidget(mode_group)

        # ── Start button ──
        content_layout.addStretch()
        start_btn = QPushButton("▶  Spiel starten")
        start_btn.setProperty("class", "primary")
        start_btn.setFixedHeight(52)
        start_font = QFont()
        start_font.setPointSize(14)
        start_btn.setFont(start_font)
        start_btn.clicked.connect(self._start_game)
        content_layout.addWidget(start_btn)

        # Root
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(toolbar)
        root_layout.addWidget(content)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def refresh_books(self) -> None:
        self._populate_books()

    def _populate_books(self) -> None:
        self._book_combo.clear()
        self._book_combo.addItem("– Fotobuch auswählen –", None)
        for book_id, name, count in self._logic.book_options():
            self._book_combo.addItem(f"{name}  ({count} Fotos)", book_id)

    def _start_game(self) -> None:
        try:
            config = self._logic.build_game_config(
                book_id=self._book_combo.currentData(),
                photo_count=self._photo_count_spin.value(),
                cols=self._cols_spin.value(),
                rows=self._rows_spin.value(),
                timer_mode=self._radio_timer.isChecked(),
                interval=self._interval_spin.value(),
            )
        except ValueError as exc:
            title = "Kein Fotobuch" if "auswählen" in str(exc) else "Leeres Fotobuch"
            QMessageBox.warning(self, title, str(exc))
            return

        self._on_start_game(config)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        self._on_back()
